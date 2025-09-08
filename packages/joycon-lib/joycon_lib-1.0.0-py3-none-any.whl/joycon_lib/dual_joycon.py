"""Dual Joy-Con support for using both controllers as one.

This module provides a class that combines input from both left and right
Joy-Cons to act as a single unified controller.
"""

from typing import Optional, Dict, Any, List, Tuple
from .joycon import JoyCon
from .buttons import ButtonState, Button
from .stick import StickState


class DualJoyCon:
    """Combines two Joy-Cons (left and right) into a single controller interface.
    
    This class manages both Joy-Cons and combines their inputs to provide
    a unified controller experience, similar to using them in the grip or
    as a Pro Controller.
    
    Attributes:
        left_joycon: Left Joy-Con controller.
        right_joycon: Right Joy-Con controller.
        button_state: Combined button state from both controllers.
    """
    
    def __init__(self, use_backend: Optional[str] = 'evdev') -> None:
        """Initialize DualJoyCon.
        
        Args:
            use_backend: Backend to use ('hid' or 'evdev').
        """
        self.left_joycon: Optional[JoyCon] = None
        self.right_joycon: Optional[JoyCon] = None
        self.button_state = ButtonState()
        self.backend = use_backend
    
    def connect(self, auto_find: bool = True,
                left_path: Optional[str] = None,
                right_path: Optional[str] = None) -> Dict[str, bool]:
        """Connect to both Joy-Cons.
        
        Args:
            auto_find: Automatically find and connect to available Joy-Cons.
            left_path: Specific device path for left Joy-Con (evdev).
            right_path: Specific device path for right Joy-Con (evdev).
        
        Returns:
            Dictionary with connection status for each Joy-Con.
            
        Raises:
            ConnectionError: If no Joy-Cons can be connected.
        """
        result = {'left': False, 'right': False}
        
        if auto_find:
            # Find all available Joy-Cons
            devices = JoyCon.list_devices(use_backend=self.backend)
            
            # Try to connect to left Joy-Con
            for device in devices:
                if self.backend == 'evdev':
                    is_left = 'left' in device.get('type', '') or '(L)' in device.get('name', '')
                else:
                    is_left = device.get('type') == 'left'
                
                if is_left and not self.left_joycon:
                    try:
                        self.left_joycon = JoyCon(use_backend=self.backend)
                        if self.backend == 'evdev':
                            self.left_joycon.connect(device_path=device['path'])
                        else:
                            self.left_joycon.connect(serial_number=device.get('serial_number'))
                        result['left'] = True
                        print(f"Connected to Left Joy-Con")
                    except Exception as e:
                        print(f"Failed to connect to left Joy-Con: {e}")
                        self.left_joycon = None
            
            # Try to connect to right Joy-Con
            for device in devices:
                if self.backend == 'evdev':
                    is_right = 'right' in device.get('type', '') or '(R)' in device.get('name', '')
                else:
                    is_right = device.get('type') == 'right'
                
                if is_right and not self.right_joycon:
                    try:
                        self.right_joycon = JoyCon(use_backend=self.backend)
                        if self.backend == 'evdev':
                            self.right_joycon.connect(device_path=device['path'])
                        else:
                            self.right_joycon.connect(serial_number=device.get('serial_number'))
                        result['right'] = True
                        print(f"Connected to Right Joy-Con")
                    except Exception as e:
                        print(f"Failed to connect to right Joy-Con: {e}")
                        self.right_joycon = None
        else:
            # Manual connection with specified paths
            if left_path:
                try:
                    self.left_joycon = JoyCon(use_backend=self.backend)
                    self.left_joycon.connect(device_path=left_path)
                    result['left'] = True
                except Exception as e:
                    print(f"Failed to connect to left Joy-Con: {e}")
            
            if right_path:
                try:
                    self.right_joycon = JoyCon(use_backend=self.backend)
                    self.right_joycon.connect(device_path=right_path)
                    result['right'] = True
                except Exception as e:
                    print(f"Failed to connect to right Joy-Con: {e}")
        
        if not result['left'] and not result['right']:
            raise ConnectionError("No Joy-Cons could be connected")
        
        return result
    
    def disconnect(self) -> None:
        """Disconnect from both Joy-Cons."""
        if self.left_joycon:
            self.left_joycon.disconnect()
            self.left_joycon = None
        
        if self.right_joycon:
            self.right_joycon.disconnect()
            self.right_joycon = None
    
    def start_polling(self, rate: int = 60) -> None:
        """Start polling both Joy-Cons.
        
        Args:
            rate: Polling rate in Hz.
        """
        if self.left_joycon:
            self.left_joycon.start_polling(rate)
        if self.right_joycon:
            self.right_joycon.start_polling(rate)
    
    def stop_polling(self) -> None:
        """Stop polling both Joy-Cons."""
        if self.left_joycon:
            self.left_joycon.stop_polling()
        if self.right_joycon:
            self.right_joycon.stop_polling()
    
    def read_input(self) -> ButtonState:
        """Read input from both Joy-Cons and combine.
        
        Returns:
            Combined ButtonState from both controllers.
        """
        # Clear previous combined state
        self.button_state.previous_buttons = self.button_state.pressed_buttons.copy()
        self.button_state.pressed_buttons.clear()
        
        # Read from left Joy-Con
        if self.left_joycon:
            left_state = self.left_joycon.read_buttons()
            self.button_state.pressed_buttons.update(left_state.pressed_buttons)
        
        # Read from right Joy-Con
        if self.right_joycon:
            right_state = self.right_joycon.read_buttons()
            self.button_state.pressed_buttons.update(right_state.pressed_buttons)
        
        return self.button_state
    
    def get_button_state(self) -> ButtonState:
        """Get combined button state from both Joy-Cons.
        
        Returns:
            Combined ButtonState.
        """
        # Combine button states from both controllers
        self.button_state.previous_buttons = self.button_state.pressed_buttons.copy()
        self.button_state.pressed_buttons.clear()
        
        if self.left_joycon:
            left_state = self.left_joycon.get_button_state()
            self.button_state.pressed_buttons.update(left_state.pressed_buttons)
        
        if self.right_joycon:
            right_state = self.right_joycon.get_button_state()
            self.button_state.pressed_buttons.update(right_state.pressed_buttons)
        
        return self.button_state
    
    def get_left_stick(self) -> StickState:
        """Get left analog stick state.
        
        Returns:
            Left stick state from left Joy-Con.
        """
        if self.left_joycon:
            return self.left_joycon.get_left_stick()
        return StickState()
    
    def get_right_stick(self) -> StickState:
        """Get right analog stick state.
        
        Returns:
            Right stick state from right Joy-Con.
        """
        if self.right_joycon:
            return self.right_joycon.get_right_stick()
        return StickState()
    
    def get_sticks(self) -> Tuple[StickState, StickState]:
        """Get both analog stick states.
        
        Returns:
            Tuple of (left_stick, right_stick).
        """
        return self.get_left_stick(), self.get_right_stick()
    
    def is_connected(self) -> Dict[str, bool]:
        """Check connection status of both Joy-Cons.
        
        Returns:
            Dictionary with connection status for each Joy-Con.
        """
        return {
            'left': self.left_joycon is not None and self.left_joycon.device.is_connected(),
            'right': self.right_joycon is not None and self.right_joycon.device.is_connected(),
            'both': (self.left_joycon is not None and self.left_joycon.device.is_connected() and
                    self.right_joycon is not None and self.right_joycon.device.is_connected())
        }
    
    def __enter__(self) -> 'DualJoyCon':
        """Context manager entry.
        
        Returns:
            Self for use in with statements.
        """
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit.
        
        Args:
            exc_type: Exception type if raised.
            exc_val: Exception value if raised.
            exc_tb: Exception traceback if raised.
        """
        self.disconnect()
    
    def __repr__(self) -> str:
        """Return string representation of DualJoyCon.
        
        Returns:
            String describing the connection status.
        """
        status = self.is_connected()
        return f"DualJoyCon(left={status['left']}, right={status['right']})"