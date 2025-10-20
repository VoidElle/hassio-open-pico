import logging

from ..models.common.common_device_model import CommonDeviceModel
from ..const import MODE_INT_TO_PRESET, MODE_PRESET_TO_INT, MODULAR_FAN_SPEED_PRESET_MODES, HUMIDITY_SELECTOR_PRESET_MODES

_LOGGER = logging.getLogger(__name__)

# Parse the CommonDeviceModel in an object readable by Home Assistant
def parse_common_device_into_readable_obj(devices: list[CommonDeviceModel]):

    # The result list
    result_list = []

    for device in devices:
        device_mode_to_preset = parse_device_mode_from_int_to_preset(device.operating_mode)
        result_list.append({
            "device_id": device.id,
            "device_type": "FAN",
            "device_name": device.name,
            "device_uid": device.serial,
            "software_version": device.firmware_version,
            "state": "OFF" if device.is_off else "ON",
            "mode": device_mode_to_preset,
            "speed": device.details.speed_rich,
            "night_mode": "ON" if device.details.night_mode == 1 else "OFF",
            "led_status": "ON" if device.details.led_on_off == 1 else "OFF",
            "selected_mode_supports_night_mode": "ON" if device_mode_to_preset in MODULAR_FAN_SPEED_PRESET_MODES else "OFF",
            "selected_mode_supports_target_humidity_control": "ON" if device_mode_to_preset in HUMIDITY_SELECTOR_PRESET_MODES else "OFF",
        })

    return result_list

# Function to retrieve the preset (string) from the mode (int)
def parse_device_mode_from_int_to_preset(mode: int) -> str:
    preset = MODE_INT_TO_PRESET.get(mode)
    if preset is None:
        _LOGGER.error(f"Unknown mode {mode}")
        raise ValueError(f"Unknown mode {mode}")
    return preset

# Function to retrieve the mode (int) from the preset (string)
def parse_device_mode_from_preset_to_int(preset: str) -> int:
    mode = MODE_PRESET_TO_INT.get(preset)
    if mode is None:
        _LOGGER.error(f"Unknown preset '{preset}'")
        raise ValueError(f"Unknown preset '{preset}'")
    return mode