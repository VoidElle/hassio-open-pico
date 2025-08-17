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
            "software_version": "2.11",
            "state": "OFF" if device.is_off else "ON",
            "mode": parse_device_mode_from_int_to_preset(device.operating_mode),
        })

    return result_list

def parse_device_mode_from_int_to_preset(mode: int) -> str:
    if mode == 1:
        return "Heat recovery"
    elif mode == 2:
        return "Extraction"
    elif mode == 3:
        return "Immission"
    elif mode == 4:
        return "Humidity - Recovery"
    elif mode == 5:
        return "Humidity - Extraction"
    elif mode == 6:
        return "Comfort summer"
    elif mode == 7:
        return "Comfort winter"
    elif mode == 8:
        return "CO2 - Recovery"
    elif mode == 9:
        return "CO2 - Extraction"
    elif mode == 10:
        return "Humidity CO2 - Recovery"
    elif mode == 11:
        return "Humidity CO2 - Extraction"
    elif mode == 12:
        return "Natural ventilation"
    else:
        _LOGGER.error(f"Unknown mode {mode}")
        raise Exception(f"Unknown mode {mode}")