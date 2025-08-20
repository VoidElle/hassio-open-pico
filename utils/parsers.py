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
            "speed": device.details.speed_rich,
            "night_mode": "ON" if device.details.night_mode == 1 else "OFF",
            "led_status": "ON" if device.details.led_on_off == 1 else "OFF",
        })

    return result_list

# Function to retrieve the preset (string) from the mode (int)
def parse_device_mode_from_int_to_preset(mode: int) -> str:
    try:

        mode_presets = {
            1: "heat_recovery",
            2: "extraction",
            3: "immission",
            4: "humidity_recovery",
            5: "humidity_extraction",
            6: "comfort_summer",
            7: "comfort_winter",
            8: "co2_recovery",
            9: "co2_extraction",
            10: "humidity_co2_recovery",
            11: "humidity_co2_extraction",
            12: "natural_ventilation",
        }

        return mode_presets[mode]
    except KeyError:
        _LOGGER.error(f"Unknown mode {mode}")
        raise ValueError(f"Unknown mode {mode}")

# Function to retrieve the mode (int) from the preset (string)
def parse_device_mode_from_preset_to_int(preset: str) -> int:
    mapping = {
        "heat_recovery": 1,
        "extraction": 2,
        "immission": 3,
        "humidity_recovery": 4,
        "humidity_extraction": 5,
        "comfort_summer": 6,
        "comfort_winter": 7,
        "co2_recovery": 8,
        "co2_extraction": 9,
        "humidity_co2_recovery": 10,
        "humidity_co2_extraction": 11,
        "natural_ventilation": 12
    }

    if preset in mapping:
        return mapping[preset]
    else:
        _LOGGER.error(f"Unknown preset '{preset}'")
        raise Exception(f"Unknown preset '{preset}'")