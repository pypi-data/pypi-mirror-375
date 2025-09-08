from typing import Tuple, Sequence, Callable

import os
import torch
import genesis as gs

from genesis_forge.genesis_env import GenesisEnv
from genesis_forge.managers.base import BaseManager
from genesis_forge.gamepads import Gamepad

CommandRangeValue = Tuple[float, float]
CommandRange = CommandRangeValue | dict[str, CommandRangeValue]

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class CommandManager(BaseManager):
    """
    Generates a command from uniform distribution of values.

    Example:
        class MyEnv(GenesisEnv):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.height_command = CommandManager(self, range=(0.1, 0.2))

            def step(self, actions: torch.Tensor):
                super().step(actions)
                # ...handle actions and rewards calculations ...

                self.command_manager.step()
                obs = self.get_observations()
                return obs, rewards, terminations, timeouts, info


            def reset(self, env_ids: Sequence[int] = None):
                super().reset(env_ids)
                # ...do reset logic here...

                self.command_manager.reset(envs_ids)
                obs = self.get_observations()
                return obs, info

            def calculate_rewards():
                target_height = self.command_manager.command
                base_pos = self.robot.get_pos()
                height_reward = torch.square(base_pos[:, 2] - target_height)

                # ...additional reward calculations here...

            def get_observations(self):
                return torch.cat(
                    [
                        self.command_manager.command,
                        # ...additional observations here...
                    ],
                    dim=-1,
                )

    Args:
        env: The environment to control
        range: The number range, or dict of ranges, to generate target command(s) for
        resample_time_s: The time interval between changing the command
    """

    def __init__(
        self,
        env: GenesisEnv,
        range: CommandRange,
        resample_time_sec: float = 5.0,
    ):
        super().__init__(env, type="command")

        self._range = range
        self.resample_time_sec = resample_time_sec
        self._external_controller = None
        self._gamepad_cfg = None
        self._gamepad_axis_command_buffer = None

        num_ranges = len(range) if isinstance(range, dict) else 1
        self._command = torch.zeros(env.num_envs, num_ranges, device=gs.device)

    """
    Properties
    """

    @property
    def command(self) -> torch.Tensor:
        """The desired command value. Shape is (num_envs, num_ranges)."""
        if self._external_controller is not None:
            return self._external_controller(self.env.step_count)
        return self._command

    @property
    def range(self) -> CommandRange:
        """The range of values to generate target command(s) for."""
        return self._range

    @range.setter
    def range(self, range: CommandRange):
        """Set the range of values to generate target command(s) for."""
        # Validate the shape of the range
        num = len(range) if isinstance(range, dict) else 1
        if num != self._command.shape[1]:
            raise ValueError(
                f"Cannot change the shape of the CommandManager range. Expected size: {self._command.shape[1]}, got {num}"
            )
        # Validate the range types match
        if type(range) != type(self._range):
            raise ValueError(
                f"Cannot change the base type of the CommandManager range. Expected type: {type(self._range)}, got {type(range)}"
            )
        # Validate that the dict keys match the current range dict keys
        if isinstance(range, dict):
            if set(range.keys()) != set(self._range.keys()):
                raise ValueError(
                    f"Cannot change the dict keys of the CommandManager range. Expected keys: {set(self._range.keys())}, got {set(range.keys())}"
                )
        self._range = range

    @property
    def resample_time_sec(self) -> float:
        """The time interval (in seconds) between changing the command for each environment."""
        return self._resample_time_sec

    @resample_time_sec.setter
    def resample_time_sec(self, resample_time_s: float):
        """Set the time interval (in seconds) between changing the command for each environment."""
        self._resample_time_sec = resample_time_s
        self._resample_steps = int(resample_time_s / self.env.dt)

    """
    Operations
    """

    def step(self):
        """Resample the command if necessary"""
        if not self.enabled or self._external_controller is not None:
            return

        resample_command_envs = (
            (self.env.episode_length % self._resample_steps == 0)
            .nonzero(as_tuple=False)
            .reshape((-1,))
        )
        self.resample_command(resample_command_envs)

    def reset(self, env_ids: Sequence[int] = None):
        """One or more environments have been reset"""
        if not self.enabled:
            return
        if env_ids is None:
            env_ids = torch.arange(self.env.num_envs, device=gs.device)
        self.resample_command(env_ids)

    def observation(self) -> torch.Tensor:
        """Function that returns the current command for each environment."""
        return self._command

    def use_external_controller(self, controller: Callable[[int], CommandRange]):
        """
        Bypass the internal command controller, and generate the command values with an external control function.
        This can be used to connect a gamepad, joystick, or other external controller to the command manager.

        Example::
            N_ENVS = 1
            MIN_HEIGHT = 0.1
            MAX_HEIGHT = 0.2

            # Create environment
            class MyEnv(GenesisEnv):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.height_command = CommandManager(self, range=(MIN_HEIGHT, MAX_HEIGHT))
                # ...

            # Setup gamepad
            gamepad = Gamepad(GAMEPAD_PRODUCT)
            cmd_buffer = torch.zeros((N_ENVS, 1), device=gs.device)
            def gamepad_controller(_step):
                a_pressed = "A" in gamepad.state.buttons
                cmd_buffer[:, 0] = MAX_HEIGHT if a_pressed else MIN_HEIGHT
                return cmd_buffer

            # Create environment & connect gamepad
            env = MyEnv(num_envs=N_ENVS)
            env.build()
            env.command_manager.use_external_controller(gamepad_controller)

        Args:
            controller: A function that takes the step index and returns a tensor of command values with the shape (num_envs, num_ranges).
        """
        self._external_controller = controller

    def use_gamepad(
        self,
        gamepad: Gamepad,
        range_axis: int | dict[str, int],
    ):
        """
        A wrapper around use_external_controller that converts a gamepad joystick axis to a command value.

        Example::
            # Create environment
            class MyEnv(GenesisEnv):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.height_command = CommandManager(self, range=(0.1, 0.2))
                # ...

            # Connect gamepad
            gamepad = Gamepad(GAMEPAD_PRODUCT)

            # Create environment & connect gamepad
            env = MyEnv(num_envs=1)
            env.build()

            # Connect joystick axis 3 to the height command
            env.command_manager.use_gamepad(gamepad_controller, range_axis=3)

        Example with multiple ranges::
            # Create environment
            class MyEnv(GenesisEnv):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.height_command = CommandManager(
                        self,
                        range={
                            "cmd1": (-2.0, 2.0),
                            "cmd2": (1.0, 5.0),
                        }
                    )
                # ...

            # Connect gamepad
            gamepad = Gamepad(GAMEPAD_PRODUCT)

            # Create environment & connect gamepad
            env = MyEnv(num_envs=1)
            env.build()

            # Connect joystick axis 2 and 3 to to the indvidual ranges
            env.command_manager.use_gamepad(
                gamepad_controller,
                range_axis={
                    "cmd1": 2,
                    "cmd2": 3,
                })


        Args:
            gamepad: The gamepad to use.
            range_axis: The axis or dict of axes to use for the command value. This should match the range init param.
        """
        self._external_controller = self._gamepad_axis_command

        # Map axis to range keys
        axis_map = []
        if isinstance(range_axis, int):
            axis_map.append(range_axis)
        elif isinstance(range_axis, dict):
            for key in self._range.keys():
                axis_map.append(range_axis[key])

        self._gamepad_cfg = {
            "gamepad": gamepad,
            "axis_map": axis_map,
        }
        self._gamepad_axis_command_buffer = torch.zeros_like(
            self._command, device=gs.device
        )

    def resample_command(self, env_ids: Sequence[int]):
        """Create a new command for the given environment ids."""
        num = torch.empty(len(env_ids), device=gs.device)

        # Get range values (this might have changed since init due to curriculum training)
        ranges = None
        if isinstance(self._range, dict):
            ranges = list(self._range.values())
        else:
            ranges = [self._range]

        # Resample the command
        for i in range(self._command.shape[1]):
            self._command[env_ids, i] = num.uniform_(*ranges[i])

    """
    Implementation
    """

    def _gamepad_axis_command(self, step_count: int) -> torch.Tensor:
        """
        Get the command from the gamepad.
        """
        if self._gamepad_cfg is None:
            return self._gamepad_axis_command_buffer

        gamepad = self._gamepad_cfg["gamepad"]
        axis_map = self._gamepad_cfg["axis_map"]

        # Convert the values to the commanded full range
        def convert_to_range(value: float, min: float, max: float) -> float:
            return (value - -1) * (max - min) / 2 + min

        # Set the gamepad commands to the buffer
        cmd = self._gamepad_axis_command_buffer
        ranges = [self._range]
        if isinstance(self._range, dict):
            ranges = list(self._range.values())
        for i, axis in enumerate(axis_map):
            if i < len(ranges):
                cmd[:, i] = convert_to_range(gamepad.state.axis(axis), *ranges[i])

        return cmd
