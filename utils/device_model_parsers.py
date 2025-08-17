from ..models.common.common_device_model import CommonDeviceModel


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
        })

    return result_list