import logging

from ..models.common.common_device_model import CommonDeviceModel

_LOGGER = logging.getLogger(__name__)

# Parse the CommonDeviceModel in an object readable by Home Assistant
def parse_common_device_into_readable_obj(devices: list[CommonDeviceModel]):

    # The result list
    result_list = []

    for device in devices:
        result_list.append({
            "device_id": device.id,
            "device_type": "FAN",
            "device_name": device.name,
            "device_uid": device.serial,
            "software_version": device.firmware_version,
            "state": "OFF" if device.is_off else "ON",
            "mode": parse_device_mode_from_int_to_preset(device.operating_mode),
            "speed": device.details.speed_row,
            "night_mode": "ON" if device.details.night_mode == 1 else "OFF",
        })

    return result_list

# Function to retrieve the preset (string) from the mode (int)
def parse_device_mode_from_int_to_preset(mode: int) -> str:
    try:

        mode_presets = {
            1: "Heat recovery",
            2: "Extraction",
            3: "Immission",
            4: "Humidity - Recovery",
            5: "Humidity - Extraction",
            6: "Comfort summer",
            7: "Comfort winter",
            8: "CO2 - Recovery",
            9: "CO2 - Extraction",
            10: "Humidity CO2 - Recovery",
            11: "Humidity CO2 - Extraction",
            12: "Natural ventilation",
        }

        return mode_presets[mode]
    except KeyError:
        _LOGGER.error(f"Unknown mode {mode}")
        raise ValueError(f"Unknown mode {mode}")

# Function to retrieve the mode (int) from the preset (string)
def parse_device_mode_from_preset_to_int(preset: str) -> int:
    mapping = {
        "Heat recovery": 1,
        "Extraction": 2,
        "Immission": 3,
        "Humidity - Recovery": 4,
        "Humidity - Extraction": 5,
        "Comfort summer": 6,
        "Comfort winter": 7,
        "CO2 - Recovery": 8,
        "CO2 - Extraction": 9,
        "Humidity CO2 - Recovery": 10,
        "Humidity CO2 - Extraction": 11,
        "Natural ventilation": 12
    }

    if preset in mapping:
        return mapping[preset]
    else:
        _LOGGER.error(f"Unknown preset '{preset}'")
        raise Exception(f"Unknown preset '{preset}'")