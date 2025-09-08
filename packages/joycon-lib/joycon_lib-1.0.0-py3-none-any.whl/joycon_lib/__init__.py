"""Joy-Con controller library for reading and decoding button information.

This library provides a Python interface for communicating with Nintendo Joy-Con
controllers, supporting buttons, analog sticks, and dual controller modes.
"""

from .joycon import JoyCon
from .dual_joycon import DualJoyCon
from .buttons import Button, ButtonState
from .stick import StickState, StickCalibration
from .exceptions import JoyConError, ConnectionError, DeviceNotFoundError

__version__ = "1.0.0"
__author__ = "JoyCon Library"
__all__ = [
    "JoyCon",
    "DualJoyCon",
    "Button", 
    "ButtonState",
    "StickState",
    "StickCalibration",
    "JoyConError",
    "ConnectionError",
    "DeviceNotFoundError"
]