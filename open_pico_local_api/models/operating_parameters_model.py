from dataclasses import dataclass

from ..enums.device_mode_enum import DeviceModeEnum
from ..enums.on_off_state_enum import OnOffStateEnum


@dataclass
class OperatingParametersModel:
    """Device operating parameters"""
    mode: DeviceModeEnum  # mod
    step_mode: int  # step_mod
    on_off: OnOffStateEnum  # on_off
    speed: int  # Current speed
    speed_requested: int  # spd_rich
    speed_row: int  # spd_row
    fan_direction: int  # fan_dir
    direction: int  # verso

    delta_temp_cycle: int  # Delta_tmprCiclo
    delta_humidity_cycle: int  # Delta_umdCiclo

    night_mode: int  # night_mod
    led_on_off: int  # led_on_off
    led_on_off_short: int  # led_on_off_breve
    led_color: int  # led_color

    chrono_mode: int  # m_crono
    timer_active: int  # tw_active

    @property
    def is_on(self) -> bool:
        """Check if device is currently on."""
        return self.on_off == OnOffStateEnum.ON

    @property
    def fan_running(self) -> bool:
        """Check if fan is currently running."""
        return self.speed > 0

    @property
    def is_night_mode_active(self) -> bool:
        """Check if night mode is active."""
        return self.night_mode == 1

    def is_led_state_on(self) -> bool:
        """Check if LED is on."""
        return self.led_on_off == 1