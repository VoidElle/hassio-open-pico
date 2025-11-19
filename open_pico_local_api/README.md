# 🌊 Open Pico Local API

> *Asynchronous Python library for Tecnosystemi Pico IoT devices*

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/yourusername/open-pico-local-api)

**[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)**

---

## ✨ Features

### 🚀 **Performance**
- Built with **asyncio** for non-blocking operations
- Efficient UDP communication protocol
- Automatic IDP synchronization

### 🔄 **Reliability**
- **Auto-reconnect** on connection failures
- Configurable retry logic
- Robust error handling

### 🎯 **Developer Friendly**
- Type-safe with Python enums
- Async context manager support
- Comprehensive logging

### 🎛️ **Full Control**
- Complete device mode management
- Fan speed control
- Humidity & LED settings

---

## 📦 Installation
1. Clone this repository in your project
2. Import PicoClient, and other relevant classes in your files

---

## 🚀 Quick Start
```python
import asyncio
from pico_client import PicoClient
from enums.device_mode_enum import DeviceModeEnum

async def main():
    # Initialize device with auto-reconnect
    device = PicoClient(
        ip="192.168.1.100",
        pin="1234",
        verbose=True,
        auto_reconnect=True
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

---

## 📚 Table of Contents

- [Configuration](#️-configuration)
- [Connection Management](#-connection-management)
- [Device Control](#️-device-control)
  - [Power Control](#power-control)
  - [Operating Modes](#operating-modes)
  - [Fan Speed](#fan-speed)
  - [Night Mode](#night-mode)
  - [LED Control](#led-control)
  - [Humidity Control](#humidity-control)
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
| `device_port` | `int` | `40070` | 📡 UDP port of the device |
| `local_port` | `int` | `40069` | 📡 Local UDP port |
| `timeout` | `float` | `15` | ⏱️ Command timeout (seconds) |
| `retry_attempts` | `int` | `3` | 🔄 Number of retry attempts |
| `retry_delay` | `float` | `2.0` | ⏳ Delay between retries (seconds) |
| `verbose` | `bool` | `False` | 📢 Enable verbose logging |
| `auto_reconnect` | `bool` | `False` | 🔌 Enable automatic reconnection |
| `max_reconnect_attempts` | `int` | `3` | 🔄 Maximum reconnection attempts |
| `reconnect_delay` | `float` | `2.0` | ⏳ Reconnection delay (seconds) |

---

## 🔌 Connection Management

### **Connect to Device**

Establishes UDP connection to the Pico device.
```python
await device.connect()
```

**Raises:** `ConnectionError` if connection fails

### **Disconnect from Device**

Gracefully closes the connection and cleans up resources.
```python
await device.disconnect()
```

### **Check Connection Status**

Returns `True` if device is currently connected.
```python
if device.connected:
    print("✓ Device is online")
```

### **Auto-Reconnect Management**

Check if auto-reconnect is enabled:
```python
if device.get_auto_reconnect():
    print("Auto-reconnect enabled")
```

Toggle auto-reconnect at runtime:
```python
device.set_auto_reconnect(True)  # Enable
device.set_auto_reconnect(False)  # Disable
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

**Returns:** Response dictionary from device

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
    async with PicoClient(ip="192.168.1.100", pin="1234") as device:
        # Turn on and set mode
        await device.turn_on()
        await device.change_operating_mode(DeviceModeEnum.HEAT_RECOVERY)
        
        # Check status
        status = await device.get_status()
        print(f"Current mode: {status.operating.mode}")
```

### Advanced Configuration

Example with advanced settings and multiple operations.
```python
async def advanced_setup():
    device = PicoClient(
        ip="192.168.1.100",
        pin="1234",
        verbose=True,
        auto_reconnect=True,
        max_reconnect_attempts=5,
        timeout=20
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
    async with PicoClient(ip="192.168.1.100", pin="1234") as device:
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
    async with PicoClient(ip="192.168.1.100", pin="1234") as device:
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
        auto_reconnect=True
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
- ✔️ Configure **auto-reconnect** for production environments
- ✔️ Handle exceptions appropriately
- ✔️ Check mode compatibility before operations
- ✔️ Verify device status after using `force` parameter

### ❌ DON'T

- ✖️ Block the event loop with synchronous operations
- ✖️ Ignore connection errors
- ✖️ Use the same client instance across multiple event loops
- ✖️ Forget to disconnect when not using context managers
- ✖️ Use `force=True` without understanding the consequences
- ✖️ Apply incompatible settings without checking device state afterwards

---

## 📦 Library Structure
```
open-pico-local-api/
├── pico_client.py              # Main client class
├── enums/
│   ├── device_mode_enum.py     # Operating modes
│   ├── on_off_state_enum.py    # Power states
│   └── target_humidity_enum.py # Humidity levels
├── models/
│   ├── pico_device_model.py           # Complete device state
│   ├── device_info_model.py           # Device identification
│   ├── sensor_readings_model.py       # Sensor data
│   ├── operating_parameters_model.py  # Operating state
│   ├── parameter_arrays_model.py      # Parameter arrays
│   └── system_info_model.py           # System diagnostics
├── utils/
│   ├── pico_protocol.py        # UDP protocol handler
│   ├── auto_reconnect.py       # Reconnection decorator
│   └── constants.py            # Mode constants
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
- **Network access** to Pico device

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

