# Preset modes that support the fan speed control
from ..enums.device_mode_enum import DeviceModeEnum

MODULAR_FAN_SPEED_PRESET_MODES = [
    DeviceModeEnum.HEAT_RECOVERY,
    DeviceModeEnum.EXTRACTION,
    DeviceModeEnum.IMMISSION,
    DeviceModeEnum.COMFORT_SUMMER,
    DeviceModeEnum.COMFORT_WINTER,
]

# Preset modes that support the selection of a desired level of humidity
HUMIDITY_SELECTOR_PRESET_MODES = [
    DeviceModeEnum.HUMIDITY_RECOVERY,
    DeviceModeEnum.HUMIDITY_EXTRACTION,
    DeviceModeEnum.HUMIDITY_CO2_RECOVERY,
    DeviceModeEnum.HUMIDITY_CO2_EXTRACTION,
]