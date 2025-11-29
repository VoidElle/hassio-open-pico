# 🌊 Open Pico Local API

> *Asynchronous Python library for Tecnosystemi Pico IoT devices*

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)](https://github.com/yourusername/open-pico-local-api)

**[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)**

> [!IMPORTANT]
> **Version 2.0.0 introduces multi-device support!** 🎉
> 
> The library now supports **simultaneous control of multiple Pico devices** through a shared transport manager with IDP range allocation. This breakthrough feature enables:
> - ✅ Multiple devices controlled from a single application
> - ✅ Concurrent polling without port conflicts
> - ✅ **Home Assistant compatibility** and integration support
> - ✅ Automatic IDP synchronization across devices

---

## ✨ Features

### 🚀 **Performance**
- Built with **asyncio** for non-blocking operations
- Efficient UDP communication protocol
- **Shared transport manager** for multiple devices
- Automatic IDP synchronization and range allocation

### 🔄 **Reliability**
- **Auto-reconnect** on connection failures
- Configurable retry logic
- Robust error handling
- **IDP sync recovery** for resilient communication

### 🎯 **Developer Friendly**
- Type-safe with Python enums
- Async context manager support
- Comprehensive logging
- **Multi-device orchestration** support

### 🎛️ **Full Control**
- Complete device mode management
- Fan speed control
- Humidity & LED settings
- **Concurrent device operations**

---

## 📦 Installation
1. Clone this repository in your project
2. Import PicoClient, and other relevant classes in your files

---

## 🚀 Quick Start

### Single Device
```python
import asyncio
from pico_client import PicoClient
from enums.device_mode_enum import DeviceModeEnum

async def main():
    # Initialize device with shared transport (default)
    device = PicoClient(
        ip="192.168.1.100",
        pin="1234",
        device_id="living_room",
        verbose=True
    )

    # Use context manager for automatic cleanup
    async with device:
        await device.turn_on()
        status = await device.get_status()
        print(f"✓ Device online: {status.operating.mode}")
        
        await device.change_operating_mode(DeviceModeEnum.CO2_RECOVERY)
        await device.change_fan_speed(75)
        print("✓ Configuration complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Multiple Devices
```python
import asyncio
from pico_client import PicoClient

async def main():
    # Create multiple device clients
    living_room = PicoClient(
        ip="192.168.1.100",
        pin="1234",
        device_id="living_room",
        verbose=True
    )
    
    bedroom = PicoClient(
        ip="192.168.1.101",
        pin="1234",
        device_id="bedroom",
        verbose=True
    )

    # Control both devices simultaneously
    async with living_room, bedroom:
        # Concurrent operations
        await asyncio.gather(
            living_room.turn_on(),
            bedroom.turn_on()
        )
        
        # Get status from both devices
        status1, status2 = await asyncio.gather(
            living_room.get_status(),
            bedroom.get_status()
        )
        
        print(f"Living Room: {status1.sensors.temperature_celsius}°C")
        print(f"Bedroom: {status2.sensors.temperature_celsius}°C")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📚 Table of Contents

- [Configuration](#️-configuration)
- [Multi-Device Support](#-multi-device-support-new)
- [Connection Management](#-connection-management)
- [Device Control](#️-device-control)
  - [Power Control](#power-control)
  - [Operating Modes](#operating-modes)
  - [Fan Speed](#fan-speed)
  - [Night Mode](#night-mode)
  - [LED Control](#led-control)
  - [Humidity Control](#humidity-control)
- [IDP Management](#-idp-management)
- [Data Models](#️-data-models)
- [Exception Handling](#-exception-handling)
- [Examples](#-examples)
- [Best Practices](#-best-practices)

---

## ⚙️ Configuration

### **Constructor Parameters**

| Parameter | Type | Default | Description |
|-----------|:----:|:-------:|-------------|
| **`ip`** ⭐ | `str` | *required* | 🌐 IP address of the Pico device |
| **`pin`** ⭐ | `str` | *required* | 🔐 PIN code for authentication |
| `device_id` | `str` | `None` | 🏷️ Unique identifier (auto-generated if not provided) |
| `device_port` | `int` | `40070` | 📡 UDP port of the device |
| `local_port` | `int` | `40069` | 📡 Local UDP port |
| `timeout` | `float` | `5` | ⏱️ Command timeout (seconds) |
| `retry_attempts` | `int` | `3` | 🔄 Number of retry attempts |
| `retry_delay` | `float` | `2.0` | ⏳ Delay between retries (seconds) |
| `verbose` | `bool` | `False` | 📢 Enable verbose logging |
| `use_shared_transport` | `bool` | `True` | 🔗 Use shared transport for multi-device support |

---

## 🔀 Multi-Device Support

Version 2.0.0 introduces a **shared transport manager** that enables multiple Pico devices to be controlled simultaneously without UDP port conflicts.

### How It Works

**IDP Range Allocation**
- Each device is assigned a unique IDP (Identifier Packet) range (10,000 IDs per device)
- The shared transport manager routes responses to the correct device based on IDP
- Automatic IDP synchronization ensures reliable communication

**Shared UDP Socket**
- All devices share a single UDP socket on the specified local port
- Responses are distributed to device-specific queues
- No port conflicts, even with multiple devices

**Automatic Management**
- Transport manager is automatically initialized on first device connection
- IDP ranges are allocated dynamically as devices register
- Cleanup happens automatically when devices disconnect

### Usage

Simply create multiple `PicoClient` instances with `use_shared_transport=True` (default):
```python
device1 = PicoClient(ip="192.168.1.100", pin="1234", device_id="device1")
device2 = PicoClient(ip="192.168.1.101", pin="1234", device_id="device2")
device3 = PicoClient(ip="192.168.1.102", pin="1234", device_id="device3")

async with device1, device2, device3:
    # All devices can be controlled concurrently
    statuses = await asyncio.gather(
        device1.get_status(),
        device2.get_status(),
        device3.get_status()
    )
```

### Device ID

The `device_id` parameter is **recommended** when using multiple devices:
- Provides meaningful identification in logs
- Used for internal routing and debugging
- Auto-generated as `{ip}:{port}` if not provided
```python
# Recommended: explicit device IDs
device1 = PicoClient(ip="192.168.1.100", pin="1234", device_id="living_room")
device2 = PicoClient(ip="192.168.1.101", pin="1234", device_id="bedroom")

# Also works: auto-generated IDs
device3 = PicoClient(ip="192.168.1.102", pin="1234")  # ID: "192.168.1.102:40070"
```

---

## 🔌 Connection Management

### **Connect to Device**

Establishes UDP connection to the Pico device. With shared transport, this registers the device with the transport manager and allocates an IDP range.
```python
await device.connect()
```

**Raises:** `ConnectionError` if connection fails

### **Disconnect from Device**

Gracefully closes the connection and cleans up resources. Unregisters from shared transport and releases IDP range.
```python
await device.disconnect()
```

### **Check Connection Status**

Returns `True` if device is currently connected.
```python
if device.connected:
    print("✓ Device is online")
```

---

## 🎛️ Device Control

### Get Device Status

Retrieve complete device state with sensor readings, operating parameters, and system information.
```python
status = await device.get_status()

# Device Information
print(f"Name: {status.device_info.name}")
print(f"Firmware: {status.device_info.firmware_full}")
print(f"IP: {status.device_info.ip}")

# Operating Status
print(f"Mode: {status.operating.mode}")
print(f"Power: {'ON' if status.is_on else 'OFF'}")
print(f"Fan Speed: {status.operating.speed}%")
print(f"Night Mode: {status.operating.is_night_mode_active}")

# Sensor Readings
print(f"Temperature: {status.sensors.temperature_celsius}°C")
print(f"Humidity: {status.sensors.humidity_percent}%")
print(f"CO2: {status.sensors.eco2} ppm")
print(f"TVOC: {status.sensors.tvoc} ppb")
print(f"Air Quality: {status.sensors.air_quality}")

# System Info
print(f"Uptime: {status.system.uptime_days:.1f} days")
print(f"Memory Free: {status.system.memory_free_kb:.1f} KB")
print(f"Health: {'Healthy' if status.is_healthy else 'Issues Detected'}")

# Feature Support
print(f"Supports Fan Control: {status.support_fan_speed_control}")
```

**Returns:** `PicoDeviceModel` with complete device state

**Parameters:**
- `retry` (bool): Enable retry logic (default: `True`)

### Power Control

Turn the device on or off.
```python
# Turn on
await device.turn_on()

# Turn off
await device.turn_off()
```

**Returns:** `CommandResponseModel` with operation result

### Operating Modes

Change the device operating mode.
```python
from enums.device_mode_enum import DeviceModeEnum

await device.change_operating_mode(DeviceModeEnum.CO2_RECOVERY)
```

**Available Modes:**
- `HEAT_RECOVERY` - Heat recovery mode
- `EXTRACTION` - Extraction only
- `IMMISSION` - Immission only
- `HUMIDITY_RECOVERY` - Humidity-based recovery
- `HUMIDITY_EXTRACTION` - Humidity-based extraction
- `COMFORT_SUMMER` - Summer comfort mode
- `COMFORT_WINTER` - Winter comfort mode
- `CO2_RECOVERY` - CO2-based recovery
- `CO2_EXTRACTION` - CO2-based extraction
- `HUMIDITY_CO2_RECOVERY` - Combined humidity/CO2 recovery
- `HUMIDITY_CO2_EXTRACTION` - Combined humidity/CO2 extraction
- `NATURAL_VENTILATION` - Natural ventilation mode

### Fan Speed

Adjust fan speed as a percentage (0-100).
```python
# Set fan speed to 50%
await device.change_fan_speed(50)

# Force change regardless of mode
await device.change_fan_speed(75, force=True)
```

**Parameters:**
- `percentage` (int): Speed from 0-100
- `retry` (bool): Enable retry logic
- `force` (bool): Skip mode validation

> ⚠️ **Note:** Only supported in certain operating modes: `HEAT_RECOVERY`, `EXTRACTION`, `IMMISSION`, `COMFORT_SUMMER`, `COMFORT_WINTER`

> 🔥 **WARNING:** Using `force=True` bypasses mode compatibility checks and may cause the device to behave unexpectedly or reset its state. Use with caution and only when you understand the implications.

### Night Mode

Activates quiet operation for nighttime use.
```python
# Enable night mode
await device.set_night_mode(True)

# Disable night mode
await device.set_night_mode(False)

# Force enable even if mode doesn't support it
await device.set_night_mode(True, force=True)
```

**Parameters:**
- `enable` (bool): True to enable, False to disable
- `retry` (bool): Enable retry logic
- `force` (bool): Skip mode validation

> ⚠️ **Note:** Only supported in modes that allow fan speed control

> 🔥 **WARNING:** Using `force=True` bypasses mode compatibility checks and may cause the device to behave unexpectedly or reset its state. Use with caution and only when you understand the implications.

### LED Control

Controls device indicator lights.
```python
# Turn off all LEDs
await device.set_led_status(False)

# Turn on LEDs
await device.set_led_status(True)
```

### Humidity Control

Set target humidity level.
```python
from enums.target_humidity_enum import TargetHumidityEnum

await device.set_target_humidity(TargetHumidityEnum.FIFTY_PERCENT)

# Force set even if mode doesn't support it
await device.set_target_humidity(TargetHumidityEnum.FIFTY_PERCENT, force=True)
```

**Parameters:**
- `target_humidity` (TargetHumidityEnum): Target humidity level
- `retry` (bool): Enable retry logic
- `force` (bool): Skip mode validation

**Available Levels:**
- `FORTY_PERCENT` - Target 40% humidity
- `FIFTY_PERCENT` - Target 50% humidity
- `SIXTY_PERCENT` - Target 60% humidity

> ⚠️ **Note:** Only supported in humidity-based modes: `HUMIDITY_RECOVERY`, `HUMIDITY_EXTRACTION`, `CO2_RECOVERY`, `CO2_EXTRACTION`

> 🔥 **WARNING:** Using `force=True` bypasses mode compatibility checks and may cause the device to behave unexpectedly or reset its state. Use with caution and only when you understand the implications.

---

## 🔢 IDP Management

The library uses **IDP (Identifier Packet)** for reliable communication between client and device.

### What is IDP?

IDP is a sequential identifier used to match commands with responses. Each device maintains its own IDP counter that must stay synchronized with the client.

### IDP Range Allocation

When using shared transport (multi-device mode):
- Each device is assigned a unique IDP range (10,000 IDs)
- Device 1: IDP 1-10,000
- Device 2: IDP 10,001-20,000
- Device 3: IDP 20,001-30,000
- And so on...

### Automatic IDP Synchronization

The library automatically handles IDP synchronization:
1. Sends command with current IDP
2. If no response, increments IDP and retries (up to 5 times)
3. If still no response, resets IDP to range start
4. Continues with full retry logic

### Manual IDP Reset

If communication becomes stuck (e.g., device was restarted), manually reset the IDP counter:
```python
# Reset IDP counter to start of allocated range
await device.reset_idp()
```

This is useful when:
- Device was power cycled
- Device firmware was updated
- Communication became persistently unresponsive

### IDP Logging

Enable verbose mode to see IDP synchronization in action:
```python
device = PicoClient(ip="192.168.1.100", pin="1234", verbose=True)

# Logs will show:
# → [living_room] SENT: stato_sync (idp:1)
# ✓ [living_room] ACK received (idp:1)
# ✓ [living_room] Response received (idp:1)
# ⚠ [living_room] No response for IDP 5 - likely out of sync
# ✓ [living_room] IDP synchronized after 2 increments
```

---

## 🏗️ Data Models

The library provides strongly-typed data models for all device information.

### **PicoDeviceModel**

Main model containing complete device state with the following components:
```python
status = await device.get_status()

# Access sub-models
status.device_info      # Device identification
status.sensors          # Sensor readings
status.operating        # Operating parameters
status.parameters       # Parameter arrays
status.system          # System information
```

### **DeviceInfoModel**

Device identification and hardware information.
```python
print(f"Name: {status.device_info.name}")
print(f"Firmware: {status.device_info.firmware_full}")
print(f"Model: {status.device_info.model}")
print(f"IP: {status.device_info.ip}")
print(f"Has Datamatrix: {status.device_info.has_datamatrix}")
```

### **SensorReadingsModel**

Real-time environmental sensor data.
```python
sensors = status.sensors

print(f"Temperature: {sensors.temperature_celsius}°C")
print(f"Humidity: {sensors.humidity_percent}%")
print(f"CO2: {sensors.eco2} ppm")
print(f"TVOC: {sensors.tvoc} ppb")
print(f"Air Quality: {sensors.air_quality}")
print(f"Has Air Quality Sensors: {sensors.has_air_quality}")
```

### **OperatingParametersModel**

Current operating state and settings.
```python
op = status.operating

print(f"Mode: {op.mode}")
print(f"Is On: {op.is_on}")
print(f"Fan Speed: {op.speed}%")
print(f"Fan Running: {op.fan_running}")
print(f"Night Mode: {op.is_night_mode_active}")
print(f"LED On: {op.is_led_state_on()}")
```

### **SystemInfoModel**

System diagnostics and health.
```python
sys = status.system

print(f"Uptime: {sys.uptime_days:.1f} days")
print(f"Memory Free: {sys.memory_free_kb:.1f} KB")
print(f"Has RTC: {sys.has_rtc}")
print(f"Date/Time: {sys.date} {sys.time}")
```

### **ParameterArraysModel**

Device parameter arrays and error tracking.
```python
params = status.parameters

print(f"Has Errors: {params.has_errors}")
print(f"Active Errors: {params.active_errors}")
print(f"Realtime Params: {params.realtime}")
```

### **CommandResponseModel**

Response from device control commands.
```python
response = await device.turn_on()

print(f"Success: {response.success}")
print(f"Message: {response.message}")
print(f"IDP: {response.idp}")
```

---

## 🚨 Exception Handling

The library provides custom exceptions for different scenarios:

| Exception | Description |
|-----------|-------------|
| `ConnectionError` | Connection establishment or communication failures |
| `TimeoutError` | Operation exceeded timeout duration |
| `NotSupportedError` | Feature not supported in current operating mode |
| `PicoDeviceError` | General device-related errors |

**Example:**
```python
from exceptions.connection_error import ConnectionError
from exceptions.not_supported_error import NotSupportedError

async def safe_operation():
    device = PicoClient(ip="192.168.1.100", pin="1234")
    
    try:
        await device.connect()
        await device.change_fan_speed(75)
        
    except NotSupportedError as e:
        print(f"⚠️  Feature not available: {e}")
        
    except ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        
    finally:
        await device.disconnect()
```

---

## 💡 Examples

### Basic Device Control

Simple example showing basic operations.
```python
async def basic_control():
    async with PicoClient(ip="192.168.1.100", pin="1234", device_id="main") as device:
        # Turn on and set mode
        await device.turn_on()
        await device.change_operating_mode(DeviceModeEnum.HEAT_RECOVERY)
        
        # Check status
        status = await device.get_status()
        print(f"Current mode: {status.operating.mode}")
```

### Multi-Device Control

Control and monitor multiple devices concurrently.
```python
async def multi_device_control():
    # Create multiple device clients
    devices = {
        "living_room": PicoClient(ip="192.168.1.100", pin="1234", device_id="living_room"),
        "bedroom": PicoClient(ip="192.168.1.101", pin="1234", device_id="bedroom"),
        "kitchen": PicoClient(ip="192.168.1.102", pin="1234", device_id="kitchen"),
    }
    
    # Connect all devices
    async with devices["living_room"], devices["bedroom"], devices["kitchen"]:
        # Turn on all devices concurrently
        await asyncio.gather(
            *[dev.turn_on() for dev in devices.values()]
        )
        
        # Set different modes for different rooms
        await asyncio.gather(
            devices["living_room"].change_operating_mode(DeviceModeEnum.COMFORT_WINTER),
            devices["bedroom"].change_operating_mode(DeviceModeEnum.HEAT_RECOVERY),
            devices["kitchen"].change_operating_mode(DeviceModeEnum.HUMIDITY_EXTRACTION)
        )
        
        # Monitor all devices
        while True:
            statuses = await asyncio.gather(
                *[dev.get_status() for dev in devices.values()],
                return_exceptions=True
            )
            
            print(f"\n{'='*60}")
            for room_name, status in zip(devices.keys(), statuses):
                if isinstance(status, Exception):
                    print(f"{room_name}: ERROR - {status}")
                else:
                    print(f"{room_name}: {status.sensors.temperature_celsius}°C, "
                          f"{status.sensors.humidity_percent}%, "
                          f"{status.operating.mode.name}")
            print(f"{'='*60}\n")
            
            await asyncio.sleep(30)
```

### Advanced Configuration

Example with advanced settings and multiple operations.
```python
async def advanced_setup():
    device = PicoClient(
        ip="192.168.1.100",
        pin="1234",
        device_id="main_unit",
        verbose=True,
        timeout=10,
        retry_attempts=5
    )
    
    async with device:
        # Enable night mode for quiet operation
        await device.set_night_mode(True)
        
        # Turn off LEDs
        await device.set_led_status(False)
        
        # Set optimal humidity
        await device.set_target_humidity(TargetHumidityEnum.FIFTY_PERCENT)
        
        # Adjust fan speed
        await device.change_fan_speed(40)
```

### Monitoring with Health Checks

Continuous monitoring with health status and error detection.
```python
async def monitor_device():
    async with PicoClient(ip="192.168.1.100", pin="1234", device_id="monitor") as device:
        while True:
            status = await device.get_status()
            
            health = "✅ Healthy" if status.is_healthy else "⚠️ Issues"
            power = '🟢 ON' if status.is_on else '🔴 OFF'
            night = '🌙 Active' if status.operating.is_night_mode_active else 'Inactive'
            
            print(f"\n📊 Device Status Report")
            print(f"Health: {health} | Power: {power}")
            print(f"Mode: {status.operating.mode.name}")
            print(f"Temperature: {status.sensors.temperature_celsius}°C")
            print(f"Humidity: {status.sensors.humidity_percent}%")
            print(f"Fan Speed: {status.operating.speed}%")
            print(f"Night Mode: {night}")
            print(f"Uptime: {status.system.uptime_days:.1f} days")
            
            # Alert on errors
            if status.parameters.has_errors:
                print(f"⚠️ Errors: {status.parameters.active_errors}")
            
            await asyncio.sleep(30)
```

### Adaptive Climate Control

Automatically adjust settings based on environmental conditions.
```python
async def adaptive_climate_control():
    async with PicoClient(ip="192.168.1.100", pin="1234", device_id="adaptive") as device:
        status = await device.get_status()
        
        # High humidity detected
        if status.sensors.humidity_percent > 70:
            print("High humidity - switching to extraction mode")
            await device.change_operating_mode(DeviceModeEnum.HUMIDITY_EXTRACTION)
            await device.change_fan_speed(80)
        
        # High CO2 levels
        elif status.sensors.eco2 > 1000:
            print("High CO2 - increasing ventilation")
            await device.change_operating_mode(DeviceModeEnum.CO2_RECOVERY)
            await device.change_fan_speed(70)
        
        # Normal conditions
        else:
            print("Normal conditions - comfort mode")
            await device.change_operating_mode(DeviceModeEnum.HEAT_RECOVERY)
            await device.change_fan_speed(50)
```

### Smart Home Integration

Example integration with daily routines.
```python
async def smart_home_automation():
    device = PicoClient(
        ip="192.168.1.100",
        pin="1234",
        device_id="automation"
    )
    
    async with device:
        # Morning routine
        print("☀️ Morning routine activated")
        await device.turn_on()
        await device.change_operating_mode(DeviceModeEnum.COMFORT_WINTER)
        await device.change_fan_speed(60)
        await device.set_led_status(True)
        
        # Wait for evening
        await asyncio.sleep(3600 * 8)
        
        # Evening routine
        print("🌙 Evening routine activated")
        await device.set_night_mode(True)
        await device.change_fan_speed(30)
        await device.set_led_status(False)
```

---

## 🎯 Best Practices

### ✅ DO

- ✔️ Use **async context managers** for automatic cleanup
- ✔️ Enable **verbose mode** during development
- ✔️ Use **explicit device_id** when controlling multiple devices
- ✔️ Handle exceptions appropriately
- ✔️ Check mode compatibility before operations
- ✔️ Verify device status after using `force` parameter
- ✔️ Use `asyncio.gather()` for concurrent operations on multiple devices

### ❌ DON'T

- ✖️ Block the event loop with synchronous operations
- ✖️ Ignore connection errors
- ✖️ Use the same client instance across multiple event loops
- ✖️ Forget to disconnect when not using context managers
- ✖️ Use `force=True` without understanding the consequences
- ✖️ Apply incompatible settings without checking device state afterwards
- ✖️ Create multiple PicoClient instances for the same device

---

## 📦 Library Structure
```
open-pico-local-api/
├── pico_client.py                     # Main client class with shared transport
├── shared_transport_manager.py        # Shared transport manager for multi-device
├── enums/
│   ├── device_mode_enum.py           # Operating modes
│   ├── on_off_state_enum.py          # Power states
│   └── target_humidity_enum.py       # Humidity levels
├── models/
│   ├── pico_device_model.py          # Complete device state
│   ├── command_response_model.py     # Command responses
│   ├── device_info_model.py          # Device identification
│   ├── sensor_readings_model.py      # Sensor data
│   ├── operating_parameters_model.py # Operating state
│   ├── parameter_arrays_model.py     # Parameter arrays
│   └── system_info_model.py          # System diagnostics
├── utils/
│   └── constants.py                  # Mode constants
└── exceptions/
    ├── connection_error.py
    ├── timeout_error.py
    ├── not_supported_error.py
    └── pico_device_error.py
```

---

## 📋 Requirements

- **Python 3.7+**
- **asyncio** support
- **Local network access** to Pico device(s)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- 🐛 **Issues**: [Report a bug](https://github.com/VoidElle/open-pico-local-api/issues)