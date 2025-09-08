"""Main Joy-Con controller interface.

This module provides the main JoyCon class for interacting with Nintendo
Joy-Con controllers.
"""

import sys
import time
import threading
from typing import Optional, Callable, Dict, Any, List
from .buttons import ButtonState, Button
from .stick import StickState
from .exceptions import ConnectionError

# Import backend based on platform
if sys.platform.startswith('linux'):
    try:
        from .evdev_backend import EvdevJoyCon, EVDEV_AVAILABLE
        backend = "evdev" if EVDEV_AVAILABLE else None
    except ImportError:
        backend = None
else:
    backend = None


class JoyCon:
    """Interface for reading button data from Joy-Con controllers.
    
    This class provides a high-level interface for connecting to and reading
    button information from Nintendo Joy-Con controllers. It handles the
    communication protocol and decodes button states.
    
    Example:
        Basic usage reading button states:
        
        >>> joycon = JoyCon()
        >>> joycon.connect()
        >>> while True:
        ...     buttons = joycon.get_button_state()
        ...     if buttons.is_pressed(Button.A):
        ...         print("A button pressed!")
        ...     time.sleep(0.016)  # ~60 FPS
    
    Attributes:
        device: Underlying device backend for communication.
        button_state: Current state of all buttons.
        is_polling: Whether the controller is actively polling for input.
    """
    
    def __init__(self, use_backend: Optional[str] = None) -> None:
        """Initialize the Joy-Con interface.
        
        Args:
            use_backend: Force specific backend ('hid' or 'evdev').
                If None, auto-detects best available backend.
        """
        self.backend_type = use_backend or backend
        
        if self.backend_type == "evdev":
            from .evdev_backend import EvdevJoyCon
            self.device = EvdevJoyCon()
        else:
            # Try evdev on Linux
            if sys.platform.startswith('linux'):
                try:
                    from .evdev_backend import EvdevJoyCon
                    self.device = EvdevJoyCon()
                    self.backend_type = "evdev"
                except ImportError:
                    raise ImportError(
                        "evdev backend not available. Install with: pip install evdev"
                    )
            else:
                raise ImportError(
                    "No backend available for this platform. "
                    "Linux requires evdev: pip install evdev"
                )
        
        self.button_state = ButtonState()
        self.is_polling = False
        self._polling_thread: Optional[threading.Thread] = None
        self._polling_rate = 60  # Hz
        self._callbacks: Dict[str, List[Callable]] = {
            'button_press': [],
            'button_release': [],
            'button_change': []
        }
    
    def connect(self, serial_number: Optional[str] = None,
                device_type: Optional[str] = None,
                device_path: Optional[str] = None) -> None:
        """Connect to a Joy-Con controller.
        
        Args:
            serial_number: Serial number of specific Joy-Con to connect to.
                If None, connects to first available Joy-Con. (HID backend only)
            device_type: Type of Joy-Con to connect to ('left', 'right', 'pro').
                If None, connects to any type.
            device_path: Path to device (evdev backend only, e.g., '/dev/input/event16').
        
        Raises:
            DeviceNotFoundError: If no matching Joy-Con is found.
            ConnectionError: If connection fails.
        
        Example:
            Connect to any available Joy-Con:
            
            >>> joycon = JoyCon()
            >>> joycon.connect()
            
            Connect to a specific left Joy-Con:
            
            >>> joycon = JoyCon()
            >>> joycon.connect(device_type='left')
        """
        # Currently only evdev backend is supported
        self.device.connect(device_path=device_path, device_type=device_type)
    
    def disconnect(self) -> None:
        """Disconnect from the Joy-Con controller.
        
        This method stops polling (if active) and closes the connection.
        """
        self.stop_polling()
        self.device.disconnect()
    
    
    def read_buttons(self) -> ButtonState:
        """Read current button state from the Joy-Con.
        
        This method performs a single read operation and updates the
        internal button state.
        
        Returns:
            Current ButtonState object.
        
        Raises:
            ConnectionError: If not connected to a device.
            CommunicationError: If reading fails.
        """
        if not self.device.is_connected():
            raise ConnectionError("Not connected to a Joy-Con")
        
        # Read buttons from device
        self.button_state = self.device.read_buttons()
        self._trigger_callbacks()
        
        return self.button_state
    
    def get_button_state(self) -> ButtonState:
        """Get the current button state without reading from device.
        
        Returns:
            Current ButtonState object.
        """
        return self.button_state
    
    def start_polling(self, rate: int = 60) -> None:
        """Start continuous polling for button updates.
        
        This method starts a background thread that continuously reads
        button states from the Joy-Con.
        
        Args:
            rate: Polling rate in Hz (default 60).
        
        Raises:
            ConnectionError: If not connected to a device.
            RuntimeError: If polling is already active.
        """
        if not self.device.is_connected():
            raise ConnectionError("Not connected to a Joy-Con")
        
        if self.is_polling:
            raise RuntimeError("Polling is already active")
        
        self._polling_rate = rate
        self.is_polling = True
        
        self._polling_thread = threading.Thread(target=self._poll_loop,
                                               daemon=True)
        self._polling_thread.start()
    
    def stop_polling(self) -> None:
        """Stop continuous polling for button updates."""
        self.is_polling = False
        
        if self._polling_thread:
            self._polling_thread.join(timeout=1.0)
            self._polling_thread = None
    
    def _poll_loop(self) -> None:
        """Internal polling loop for continuous button reading."""
        interval = 1.0 / self._polling_rate
        
        while self.is_polling:
            try:
                self.read_buttons()
            except Exception:
                # Silently ignore errors in polling thread
                pass
            
            time.sleep(interval)
    
    def register_callback(self, event_type: str,
                         callback: Callable[[Button], None]) -> None:
        """Register a callback for button events.
        
        Args:
            event_type: Type of event ('button_press', 'button_release',
                or 'button_change').
            callback: Function to call when event occurs.
                Should accept a Button parameter.
        
        Raises:
            ValueError: If event_type is invalid.
        
        Example:
            Register a callback for button presses:
            
            >>> def on_press(button):
            ...     print(f"{button.name} pressed!")
            >>> joycon.register_callback('button_press', on_press)
        """
        if event_type not in self._callbacks:
            raise ValueError(f"Invalid event type: {event_type}")
        
        self._callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: str,
                           callback: Callable[[Button], None]) -> None:
        """Unregister a callback for button events.
        
        Args:
            event_type: Type of event.
            callback: Callback function to remove.
        """
        if event_type in self._callbacks:
            try:
                self._callbacks[event_type].remove(callback)
            except ValueError:
                pass
    
    def _trigger_callbacks(self) -> None:
        """Trigger appropriate callbacks based on button state changes."""
        for button in Button:
            if self.button_state.just_pressed(button):
                for callback in self._callbacks['button_press']:
                    callback(button)
                for callback in self._callbacks['button_change']:
                    callback(button)
            
            elif self.button_state.just_released(button):
                for callback in self._callbacks['button_release']:
                    callback(button)
                for callback in self._callbacks['button_change']:
                    callback(button)
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the connected Joy-Con.
        
        Returns:
            Dictionary containing device information:
                - connected: Whether a device is connected
                - backend: Backend being used
                - Additional device-specific information
        """
        info = self.device.get_device_info()
        info['backend'] = self.backend_type
        return info
    
    @classmethod
    def list_devices(cls, use_backend: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available Joy-Con devices.
        
        Args:
            use_backend: Backend to use (currently only 'evdev' supported).
                If None, uses default backend.
        
        Returns:
            List of dictionaries containing device information.
        
        Example:
            List all connected Joy-Cons:
            
            >>> devices = JoyCon.list_devices()
            >>> for device in devices:
            ...     print(f"{device['type']} Joy-Con")
        """
        backend_to_use = use_backend or backend or "evdev"
        
        if backend_to_use == "evdev":
            from .evdev_backend import EvdevJoyCon
            return EvdevJoyCon.list_devices()
        else:
            return []
    
    def __enter__(self) -> 'JoyCon':
        """Context manager entry.
        
        Returns:
            Self for use in with statements.
        
        Example:
            Using Joy-Con with context manager:
            
            >>> with JoyCon() as joycon:
            ...     joycon.connect()
            ...     buttons = joycon.read_buttons()
            ...     print(buttons.get_pressed_names())
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
    
    def get_left_stick(self) -> StickState:
        """Get the current left analog stick state.
        
        Returns:
            StickState object with current stick position.
        """
        return self.device.get_left_stick()
    
    def get_right_stick(self) -> StickState:
        """Get the current right analog stick state.
        
        Returns:
            StickState object with current stick position.
        """
        return self.device.get_right_stick()
    
    def __repr__(self) -> str:
        """Return string representation of JoyCon.
        
        Returns:
            String describing the Joy-Con connection status.
        """
        if self.device.is_connected():
            info = self.get_device_info()
            return f"JoyCon(connected=True, backend='{self.backend_type}', info={info})"
        return f"JoyCon(connected=False, backend='{self.backend_type}')"