"""Button definitions and state management for Joy-Con controllers.

This module provides enumerations and classes for managing Joy-Con button states.
"""

from enum import IntEnum
from typing import Dict, List, Set


class Button(IntEnum):
    """Enumeration of all Joy-Con buttons.
    
    These values correspond to bit positions in the button state bytes
    received from the Joy-Con controller.
    """
    
    # Right Joy-Con buttons
    Y = 0x01
    X = 0x02
    B = 0x04
    A = 0x08
    SR_RIGHT = 0x10
    SL_RIGHT = 0x20
    R = 0x40
    ZR = 0x80
    
    # Shared buttons
    MINUS = 0x100
    PLUS = 0x200
    R_STICK = 0x400
    L_STICK = 0x800
    HOME = 0x1000
    CAPTURE = 0x2000
    
    # Left Joy-Con buttons
    DOWN = 0x10000
    UP = 0x20000
    RIGHT = 0x40000
    LEFT = 0x80000
    SR_LEFT = 0x100000
    SL_LEFT = 0x200000
    L = 0x400000
    ZL = 0x800000


class ButtonState:
    """Manages the state of Joy-Con buttons.
    
    This class tracks which buttons are currently pressed and provides
    methods to update and query button states.
    
    Attributes:
        pressed_buttons: Set of currently pressed buttons.
        previous_buttons: Set of buttons pressed in the previous frame.
    """
    
    def __init__(self) -> None:
        """Initialize ButtonState with no buttons pressed."""
        self.pressed_buttons: Set[Button] = set()
        self.previous_buttons: Set[Button] = set()
    
    def update(self, button_data: bytes) -> None:
        """Update button state from raw HID data.
        
        Args:
            button_data: 3 bytes of button data from Joy-Con HID report.
                Byte 0: Right Joy-Con buttons
                Byte 1: Shared buttons
                Byte 2: Left Joy-Con buttons
        
        Raises:
            ValueError: If button_data is not exactly 3 bytes.
        """
        if len(button_data) != 3:
            raise ValueError(f"Expected 3 bytes of button data, got {len(button_data)}")
        
        self.previous_buttons = self.pressed_buttons.copy()
        self.pressed_buttons.clear()
        
        # Decode right Joy-Con buttons (byte 0)
        right_buttons = button_data[0]
        if right_buttons & 0x01:
            self.pressed_buttons.add(Button.Y)
        if right_buttons & 0x02:
            self.pressed_buttons.add(Button.X)
        if right_buttons & 0x04:
            self.pressed_buttons.add(Button.B)
        if right_buttons & 0x08:
            self.pressed_buttons.add(Button.A)
        if right_buttons & 0x10:
            self.pressed_buttons.add(Button.SR_RIGHT)
        if right_buttons & 0x20:
            self.pressed_buttons.add(Button.SL_RIGHT)
        if right_buttons & 0x40:
            self.pressed_buttons.add(Button.R)
        if right_buttons & 0x80:
            self.pressed_buttons.add(Button.ZR)
        
        # Decode shared buttons (byte 1)
        shared_buttons = button_data[1]
        if shared_buttons & 0x01:
            self.pressed_buttons.add(Button.MINUS)
        if shared_buttons & 0x02:
            self.pressed_buttons.add(Button.PLUS)
        if shared_buttons & 0x04:
            self.pressed_buttons.add(Button.R_STICK)
        if shared_buttons & 0x08:
            self.pressed_buttons.add(Button.L_STICK)
        if shared_buttons & 0x10:
            self.pressed_buttons.add(Button.HOME)
        if shared_buttons & 0x20:
            self.pressed_buttons.add(Button.CAPTURE)
        
        # Decode left Joy-Con buttons (byte 2)
        left_buttons = button_data[2]
        if left_buttons & 0x01:
            self.pressed_buttons.add(Button.DOWN)
        if left_buttons & 0x02:
            self.pressed_buttons.add(Button.UP)
        if left_buttons & 0x04:
            self.pressed_buttons.add(Button.RIGHT)
        if left_buttons & 0x08:
            self.pressed_buttons.add(Button.LEFT)
        if left_buttons & 0x10:
            self.pressed_buttons.add(Button.SR_LEFT)
        if left_buttons & 0x20:
            self.pressed_buttons.add(Button.SL_LEFT)
        if left_buttons & 0x40:
            self.pressed_buttons.add(Button.L)
        if left_buttons & 0x80:
            self.pressed_buttons.add(Button.ZL)
    
    def is_pressed(self, button: Button) -> bool:
        """Check if a button is currently pressed.
        
        Args:
            button: The button to check.
        
        Returns:
            True if the button is currently pressed, False otherwise.
        """
        return button in self.pressed_buttons
    
    def is_released(self, button: Button) -> bool:
        """Check if a button is currently released.
        
        Args:
            button: The button to check.
        
        Returns:
            True if the button is not pressed, False otherwise.
        """
        return button not in self.pressed_buttons
    
    def just_pressed(self, button: Button) -> bool:
        """Check if a button was just pressed this frame.
        
        Args:
            button: The button to check.
        
        Returns:
            True if the button was pressed this frame but not the previous frame.
        """
        return button in self.pressed_buttons and button not in self.previous_buttons
    
    def just_released(self, button: Button) -> bool:
        """Check if a button was just released this frame.
        
        Args:
            button: The button to check.
        
        Returns:
            True if the button was released this frame but pressed the previous frame.
        """
        return button not in self.pressed_buttons and button in self.previous_buttons
    
    def get_pressed_buttons(self) -> List[Button]:
        """Get a list of all currently pressed buttons.
        
        Returns:
            List of pressed Button enum values.
        """
        return list(self.pressed_buttons)
    
    def get_pressed_names(self) -> List[str]:
        """Get a list of names of all currently pressed buttons.
        
        Returns:
            List of button names as strings.
        """
        return [button.name for button in self.pressed_buttons]
    
    def to_dict(self) -> Dict[str, bool]:
        """Convert button state to a dictionary.
        
        Returns:
            Dictionary mapping button names to their pressed state.
        """
        return {
            button.name: self.is_pressed(button)
            for button in Button
        }
    
    def __repr__(self) -> str:
        """Return string representation of button state.
        
        Returns:
            String showing pressed buttons.
        """
        if self.pressed_buttons:
            return f"ButtonState(pressed={self.get_pressed_names()})"
        return "ButtonState(pressed=[])"