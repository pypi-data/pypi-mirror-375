"""Evdev backend for Joy-Con communication on Linux.

This module provides Joy-Con communication through the Linux evdev interface,
which works with the hid_nintendo kernel driver.
"""

import time
import threading
from typing import Optional, List, Dict, Any
from .buttons import ButtonState, Button
from .stick import StickState, StickCalibration
from .exceptions import DeviceNotFoundError, ConnectionError

try:
    from evdev import InputDevice, categorize, ecodes, list_devices
    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False


class EvdevJoyCon:
    """Manages Joy-Con communication via Linux evdev interface.
    
    This class provides an alternative to HID communication by using the
    Linux input subsystem (evdev) with the hid_nintendo kernel driver.
    
    Attributes:
        BUTTON_MAP: Mapping from evdev button codes to Joy-Con Button enum.
    """
    
    # Map evdev button codes to our Button enum
    # Using raw codes since some constants might not be defined
    BUTTON_MAP_LEFT = {
        # Left Joy-Con D-pad (codes 544-547)
        544: Button.UP,      # BTN_DPAD_UP
        545: Button.DOWN,    # BTN_DPAD_DOWN
        546: Button.LEFT,    # BTN_DPAD_LEFT
        547: Button.RIGHT,   # BTN_DPAD_RIGHT
        
        # Left Joy-Con buttons (corrected based on actual testing)
        310: Button.L,       # BTN_TL -> L
        312: Button.ZL,      # BTN_TL2 -> ZL
        311: Button.SL_LEFT, # BTN_TR -> SL (when held sideways)
        313: Button.SR_LEFT, # BTN_TR2 -> SR (when held sideways)
        314: Button.MINUS,   # BTN_SELECT -> MINUS
        317: Button.L_STICK, # BTN_THUMBL -> L_STICK
        309: Button.CAPTURE, # BTN_Z -> CAPTURE
    }
    
    BUTTON_MAP_RIGHT = {
        # Right Joy-Con face buttons (swapped A/B based on user feedback)
        304: Button.B,       # BTN_SOUTH -> B (was incorrectly A)
        305: Button.A,       # BTN_EAST -> A (was incorrectly B)
        307: Button.X,       # BTN_NORTH -> X
        308: Button.Y,       # BTN_WEST -> Y
        
        # Right Joy-Con shoulder buttons (corrected based on user feedback)
        311: Button.R,         # BTN_TR -> R
        313: Button.ZR,        # BTN_TR2 -> ZR (was incorrectly SL_RIGHT)
        312: Button.SR_RIGHT,  # BTN_TL2 -> SR (when held sideways)
        310: Button.SL_RIGHT,  # BTN_TL -> SL (when held sideways)
        315: Button.PLUS,      # BTN_START -> PLUS
        316: Button.HOME,      # BTN_MODE -> HOME
        318: Button.R_STICK,   # BTN_THUMBR -> R_STICK
    }
    
    # Combined map for Pro Controller
    BUTTON_MAP = {
        **BUTTON_MAP_LEFT,
        **BUTTON_MAP_RIGHT,
        # Additional Pro Controller mappings if needed
    }
    
    # Alternative mappings for different kernel versions
    BUTTON_MAP_ALT = {
        ecodes.BTN_0: Button.B,
        ecodes.BTN_1: Button.A,
        ecodes.BTN_2: Button.Y,
        ecodes.BTN_3: Button.X,
    }
    
    def __init__(self) -> None:
        """Initialize EvdevJoyCon.
        
        Raises:
            ImportError: If evdev is not installed.
        """
        if not EVDEV_AVAILABLE:
            raise ImportError(
                "evdev library not installed. "
                "Install with: pip install evdev"
            )
        
        self.device: Optional[InputDevice] = None
        self.device_type: Optional[str] = None  # 'left', 'right', or 'pro'
        self.button_state = ButtonState()
        self.left_stick = StickState()
        self.right_stick = StickState()
        self.stick_calibration = StickCalibration()
        self.is_polling = False
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_x = 0
        self._current_y = 0
    
    @classmethod
    def list_devices(cls) -> List[Dict[str, Any]]:
        """List all available Joy-Con devices.
        
        Returns:
            List of dictionaries containing device information.
        """
        if not EVDEV_AVAILABLE:
            return []
        
        devices = []
        
        for path in list_devices():
            try:
                device = InputDevice(path)
                if 'Joy-Con' in device.name or 'Nintendo' in device.name:
                    device_type = 'unknown'
                    if '(L)' in device.name:
                        device_type = 'left'
                    elif '(R)' in device.name:
                        device_type = 'right'
                    elif 'Pro Controller' in device.name:
                        device_type = 'pro'
                    
                    # Skip IMU-only devices as they don't have buttons
                    if '(IMU)' not in device.name:
                        devices.append({
                            'path': device.path,
                            'name': device.name,
                            'type': device_type,
                            'phys': device.phys,
                        })
                device.close()
            except Exception:
                continue
        
        return devices
    
    def connect(self, device_path: Optional[str] = None,
                device_type: Optional[str] = None) -> None:
        """Connect to a Joy-Con device.
        
        Args:
            device_path: Path to the device (e.g., '/dev/input/event16').
                If None, connects to first available Joy-Con.
            device_type: Type of Joy-Con to connect to ('left', 'right', 'pro').
                If None, connects to any type.
        
        Raises:
            DeviceNotFoundError: If no matching device is found.
            ConnectionError: If connection fails.
        """
        devices = self.list_devices()
        
        if not devices:
            raise DeviceNotFoundError(
                "No Joy-Con devices found. "
                "Make sure hid_nintendo driver is loaded: "
                "sudo modprobe hid_nintendo"
            )
        
        target_device = None
        
        if device_path:
            # Find device by path
            for device in devices:
                if device['path'] == device_path:
                    target_device = device
                    break
        else:
            # Find device by type or use first available
            for device in devices:
                if device_type and device['type'] != device_type:
                    continue
                target_device = device
                break
        
        if not target_device:
            raise DeviceNotFoundError(
                f"No Joy-Con found matching criteria "
                f"(path={device_path}, type={device_type})"
            )
        
        try:
            self.device = InputDevice(target_device['path'])
            # Store the device type for proper axis mapping
            self.device_type = target_device['type']
        except PermissionError:
            raise ConnectionError(
                f"Permission denied accessing {target_device['path']}. "
                f"Try: sudo chmod 666 {target_device['path']} "
                f"or run with sudo"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the Joy-Con device."""
        self.stop_polling()
        
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None
    
    def read_buttons(self) -> ButtonState:
        """Read current button state from the Joy-Con.
        
        This method performs a non-blocking read and updates the button state
        based on any available events.
        
        Returns:
            Current ButtonState object.
        
        Raises:
            ConnectionError: If not connected to a device.
        """
        if not self.device:
            raise ConnectionError("Not connected to a Joy-Con")
        
        try:
            # Use select with 0 timeout for immediate non-blocking check
            import select
            r, w, x = select.select([self.device], [], [], 0)
            
            if self.device in r:
                # Read all available events at once for lower latency
                for event in self.device.read():
                    if event.type == ecodes.EV_KEY:
                        self._process_button_event(event)
                    elif event.type == ecodes.EV_ABS:
                        self._process_axis_event(event)
        except BlockingIOError:
            # No events available, which is normal
            pass
        except OSError:
            # Device disconnected
            raise ConnectionError("Joy-Con disconnected")
        except Exception:
            # Other errors - continue silently
            pass
        
        return self.button_state
    
    def _process_button_event(self, event) -> None:
        """Process a button event from evdev.
        
        Args:
            event: Evdev InputEvent object.
        """
        # Choose the correct button map based on device type
        if self.device_type == 'left':
            button = self.BUTTON_MAP_LEFT.get(event.code)
        elif self.device_type == 'right':
            button = self.BUTTON_MAP_RIGHT.get(event.code)
        else:
            # Pro controller or unknown - use combined map
            button = self.BUTTON_MAP.get(event.code)
        
        if not button:
            button = self.BUTTON_MAP_ALT.get(event.code)
        
        if button:
            # Update previous state for change detection
            self.button_state.previous_buttons = self.button_state.pressed_buttons.copy()
            
            # Directly update pressed buttons set
            if event.value == 1:  # Button pressed
                self.button_state.pressed_buttons.add(button)
            elif event.value == 0:  # Button released
                self.button_state.pressed_buttons.discard(button)
    
    def _process_axis_event(self, event) -> None:
        """Process an axis event from evdev (analog sticks).
        
        Args:
            event: Evdev InputEvent object.
        """
        # Joy-Con (L) has its stick on ABS_X/ABS_Y
        # Joy-Con (R) has its stick on ABS_X/ABS_Y (not ABS_RX/RY!)
        # Pro Controller has left stick on ABS_X/ABS_Y and right stick on ABS_RX/ABS_RY
        
        if self.device_type == 'left':
            # Left Joy-Con: stick is the left stick
            if event.code == ecodes.ABS_X:
                self._current_x = event.value
                self.left_stick = self.stick_calibration.process(self._current_x, self._current_y)
            elif event.code == ecodes.ABS_Y:
                self._current_y = event.value
                self.left_stick = self.stick_calibration.process(self._current_x, self._current_y)
                
        elif self.device_type == 'right':
            # Right Joy-Con: uses ABS_RX (3) and ABS_RY (4) for its stick!
            if event.code == 3:  # ABS_RX
                self._current_x = event.value
                self.right_stick = self.stick_calibration.process(self._current_x, self._current_y)
            elif event.code == 4:  # ABS_RY
                self._current_y = event.value
                self.right_stick = self.stick_calibration.process(self._current_x, self._current_y)
                
        else:  # Pro controller or unknown
            # Pro Controller has both sticks
            if event.code == ecodes.ABS_X:
                self._current_x = event.value
                self.left_stick = self.stick_calibration.process(self._current_x, self._current_y)
            elif event.code == ecodes.ABS_Y:
                self._current_y = event.value
                self.left_stick = self.stick_calibration.process(self._current_x, self._current_y)
            elif hasattr(ecodes, 'ABS_RX') and event.code == ecodes.ABS_RX:
                # Right stick X for Pro Controller
                # Note: some evdev versions might not have ABS_RX
                pass  # TODO: implement if needed
            elif hasattr(ecodes, 'ABS_RY') and event.code == ecodes.ABS_RY:
                # Right stick Y for Pro Controller  
                pass  # TODO: implement if needed
    
    
    def start_polling(self, rate: int = 60) -> None:
        """Start continuous polling for button updates.
        
        Args:
            rate: Polling rate in Hz (default 60).
        
        Raises:
            ConnectionError: If not connected to a device.
            RuntimeError: If polling is already active.
        """
        if not self.device:
            raise ConnectionError("Not connected to a Joy-Con")
        
        if self.is_polling:
            raise RuntimeError("Polling is already active")
        
        self.is_polling = True
        self._stop_event.clear()
        
        self._polling_thread = threading.Thread(
            target=self._poll_loop,
            args=(1.0 / rate,),
            daemon=True
        )
        self._polling_thread.start()
    
    def stop_polling(self) -> None:
        """Stop continuous polling for button updates."""
        self.is_polling = False
        self._stop_event.set()
        
        if self._polling_thread:
            self._polling_thread.join(timeout=1.0)
            self._polling_thread = None
    
    def _poll_loop(self, interval: float) -> None:
        """Internal polling loop for continuous button reading.
        
        Args:
            interval: Time between polls in seconds.
        """
        import select
        
        # Try to grab device for exclusive access (lower latency)
        grabbed = False
        try:
            self.device.grab()
            grabbed = True
        except:
            pass  # Continue without exclusive access if grab fails
        
        try:
            # Use select for low-latency event reading
            while not self._stop_event.is_set():
                try:
                    # Wait for events with timeout
                    r, w, x = select.select([self.device], [], [], interval)
                    
                    if self.device in r:
                        # Read all available events at once for efficiency
                        for event in self.device.read():
                            if event.type == ecodes.EV_KEY:
                                self._process_button_event(event)
                            elif event.type == ecodes.EV_ABS:
                                self._process_axis_event(event)
                except OSError:
                    # Device disconnected
                    break
                except Exception:
                    # For other exceptions, continue with minimal delay
                    time.sleep(0.001)  # 1ms sleep instead of full interval
        finally:
            # Always ungrab if we grabbed
            if grabbed:
                try:
                    self.device.ungrab()
                except:
                    pass
    
    def is_connected(self) -> bool:
        """Check if connected to a Joy-Con device.
        
        Returns:
            True if connected, False otherwise.
        """
        return self.device is not None
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the connected Joy-Con.
        
        Returns:
            Dictionary containing device information.
        """
        if not self.device:
            return {'connected': False}
        
        return {
            'connected': True,
            'name': self.device.name,
            'path': self.device.path,
            'phys': self.device.phys,
        }
    
    def get_left_stick(self) -> StickState:
        """Get the current left stick state.
        
        Returns:
            StickState object for the left analog stick.
        """
        return self.left_stick
    
    def get_right_stick(self) -> StickState:
        """Get the current right stick state.
        
        Returns:
            StickState object for the right analog stick.
        """
        return self.right_stick