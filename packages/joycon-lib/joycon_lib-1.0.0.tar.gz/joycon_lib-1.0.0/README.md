# Joy-Con Python Library

A Linux-based Python library for reading and decoding button information from Nintendo Joy-Con controllers using the evdev interface.

> **Note:** This library currently only supports Linux. Windows and macOS support would require implementing HID or other platform-specific backends.

## Features

- **Linux Support** - Works on Linux with the evdev interface
- **Evdev Backend** - Direct communication with Joy-Con controllers via Linux input subsystem
- **Real-time Input** - Read button states and analog sticks in real-time
- **Multiple Controllers** - Support for left, right, and Pro controllers
- **Dual Joy-Con Mode** - Use two Joy-Cons as a single controller
- **Event System** - Register callbacks for button press/release events
- **Polling Mode** - Continuous input monitoring at configurable rates
- **Clean API** - Simple, intuitive interface with Google-style docstrings
- **Low Latency** - Optimized for minimal input lag with device grabbing and efficient event reading

## Requirements

- Python 3.10 or higher
- Linux operating system
- Bluetooth-connected Joy-Con controllers
- Dependencies installed automatically:
  - `evdev` (Linux event device interface)

## Installation


```bash
pip install joycon-lib
```


### Prerequisites - Bluetooth Setup

#### Linux Setup

Before using the library, you need to set up your Linux system:

**1. Enable the hid_nintendo kernel driver (REQUIRED):**

```bash
# Load the driver - this is required for Joy-Con support
sudo modprobe hid_nintendo

# To load automatically on boot (recommended):
echo "hid_nintendo" | sudo tee /etc/modules-load.d/hid_nintendo.conf
```

> **Note:** Without the `hid_nintendo` driver, Joy-Con controllers won't be recognized as input devices.

**2. Add udev rules for non-root access (RECOMMENDED):**

Without these rules, you'll need to run your Python scripts with `sudo`.

```bash
# Create udev rules file
sudo tee /etc/udev/rules.d/50-joycon.rules << 'EOF'
# Nintendo Joy-Con (L/R) and Pro Controller
KERNEL=="event*", ATTRS{name}=="*Joy-Con*", MODE="0666"
KERNEL=="event*", ATTRS{name}=="*Pro Controller*", MODE="0666"
EOF

# Reload and apply rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**3. Connect Joy-Con via Bluetooth:**
```bash
# Open Bluetooth control
bluetoothctl

# In bluetoothctl:
power on
agent on
default-agent
scan on

# Press sync button on Joy-Con (small button between SL/SR)
# Wait for Joy-Con to appear, note the MAC address

pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX

# Exit bluetoothctl
exit
```

Or you can use the GUI to connect to the Joy-Con device via Bluetooth.

## Quick Start

### Basic Usage

```python
from joycon_lib import JoyCon, Button
import time

# Create and connect to Joy-Con
joycon = JoyCon(use_backend='evdev')  # Linux only
joycon.connect()  # Auto-finds first available Joy-Con

# Read button states
while True:
    buttons = joycon.read_buttons()
    if buttons.is_pressed(Button.A):
        print("A button pressed!")
    time.sleep(0.016)  # ~60 FPS

# Disconnect when done
joycon.disconnect()
```

### Dual Joy-Con Mode

```python
from joycon_lib import DualJoyCon, Button
import time

# Create dual Joy-Con controller
dual = DualJoyCon(use_backend='evdev')  # Linux only
dual.connect(auto_find=True)  # Auto-finds and connects both Joy-Cons

# Start polling
dual.start_polling(rate=60)

# Read from both controllers as one
while True:
    buttons = dual.get_button_state()  # Combined buttons from both
    left_stick, right_stick = dual.get_sticks()  # Both analog sticks
    
    if buttons.is_pressed(Button.A):
        print("A pressed!")
    if buttons.is_pressed(Button.L) and buttons.is_pressed(Button.R):
        print("L+R combo!")
    
    time.sleep(0.016)

dual.disconnect()
```

## Running Examples

### Quick Test

```bash
# Run the library's built-in test
python -m joycon_lib
```

### Example Scripts

The `examples/` directory contains various demonstration scripts:

| Script | Description |
|--------|-------------|
| `example_stick.py` | Test analog stick input |
| `example_dual.py` | Use both Joy-Cons independently |
| `example_evdev.py` | Test evdev backend (Linux only) |

```bash
cd examples/
python example_dual.py  # Start with the interactive demo
```

## API Reference

### Core Classes

#### `JoyCon`

Main interface for single Joy-Con interaction.

**Methods:**
- `connect(device_path=None, device_type=None)` - Connect to a Joy-Con (evdev backend)
- `disconnect()` - Disconnect from the Joy-Con
- `read_buttons()` - Read current button state from device
- `get_button_state()` - Get current button state without reading
- `get_left_stick()` - Get left analog stick state
- `get_right_stick()` - Get right analog stick state
- `start_polling(rate=60)` - Start continuous polling
- `stop_polling()` - Stop polling
- `register_callback(event_type, callback)` - Register event callback
- `list_devices()` - List all available Joy-Con devices
- `get_device_info()` - Get information about connected device

#### `DualJoyCon`

Manages two Joy-Cons as a single controller.

**Methods:**
- `connect(auto_find=True, left_path=None, right_path=None)` - Connect to both Joy-Cons
- `disconnect()` - Disconnect both controllers
- `read_input()` - Read input from both Joy-Cons and combine
- `get_button_state()` - Get combined button state without reading
- `get_left_stick()` - Get left analog stick position
- `get_right_stick()` - Get right analog stick position
- `get_sticks()` - Get both analog stick positions as tuple
- `start_polling(rate=60)` - Start polling both controllers
- `stop_polling()` - Stop polling
- `is_connected()` - Check connection status of both Joy-Cons

#### `ButtonState`

Represents the current state of all buttons.

**Methods:**
- `is_pressed(button)` - Check if button is currently pressed
- `is_released(button)` - Check if button is currently released
- `just_pressed(button)` - Check if button was just pressed this frame
- `just_released(button)` - Check if button was just released this frame
- `get_pressed_names()` - Get list of pressed button names
- `to_dict()` - Convert button state to dictionary

### Button Mappings

| Controller | Buttons |
|------------|---------|
| **Right Joy-Con** | `Y`, `X`, `B`, `A`, `SR_RIGHT`, `SL_RIGHT`, `R`, `ZR`, `PLUS`, `R_STICK`, `HOME` |
| **Left Joy-Con** | `UP`, `DOWN`, `LEFT`, `RIGHT`, `SR_LEFT`, `SL_LEFT`, `L`, `ZL`, `MINUS`, `L_STICK`, `CAPTURE` |
| **Pro Controller** | All of the above |

#### `StickState`

Represents analog stick position and provides utility methods.

**Methods:**
- `get_angle()` - Get stick angle in degrees (0-360)
- `get_magnitude()` - Get displacement from center (0.0-1.0)
- `is_centered(deadzone=0.1)` - Check if stick is centered
- `get_direction_4way()` - Get 4-way directional input
- `get_direction_8way()` - Get 8-way directional input

**Attributes:**
- `x` - X-axis value (-1.0 to 1.0)
- `y` - Y-axis value (-1.0 to 1.0)
- `raw_x` - Raw X value from controller
- `raw_y` - Raw Y value from controller

## Troubleshooting

### Common Issues

**Joy-Con not detected:**
- Ensure Joy-Con is paired via Bluetooth
- Check battery level
- Try re-pairing the controller
- On Linux, verify udev rules are installed

**Permission denied errors (Linux):**
- Add udev rules as shown in setup
- Run with `sudo` (not recommended)
- Ensure `hid_nintendo` kernel module is loaded

**Connection drops:**
- Keep Joy-Con within Bluetooth range
- Check for interference from other devices
- Ensure Joy-Con firmware is up to date

## License

MIT License - See [LICENSE](LICENSE) file for details