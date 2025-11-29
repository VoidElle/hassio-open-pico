from dataclasses import dataclass
from typing import Dict, Any

from ..enums.device_mode_enum import DeviceModeEnum
from ..enums.on_off_state_enum import OnOffStateEnum
from ..enums.target_humidity_enum import TargetHumidityEnum
from .device_info_model import DeviceInfoModel
from .operating_parameters_model import OperatingParametersModel
from .parameter_arrays_model import ParameterArraysModel
from .sensor_readings_model import SensorReadingsModel
from .system_info_model import SystemInfoModel
from ..utils.constants import MODULAR_FAN_SPEED_PRESET_MODES, HUMIDITY_SELECTOR_PRESET_MODES


@dataclass
class PicoDeviceModel:
    """
    Complete Pico device status

    Provides structured access to all device data with type hints,
    helper methods, and property accessors.
    """

    # Protocol fields
    idp: int
    frame_from: str  # frm
    command: str  # cmd
    response: int  # res

    # Device components
    device_info: DeviceInfoModel
    sensors: SensorReadingsModel
    parameters: ParameterArraysModel
    operating: OperatingParametersModel
    system: SystemInfoModel

    # Raw data for advanced access
    raw_data: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PicoDeviceModel':
        """
        Create PicoStatus from device response dictionary

        Args:
            data: Raw device status dictionary

        Returns:
            PicoStatus instance

        Example:
            >>> status = PicoDeviceModel.from_dict(device_response)
            >>> print(status.sensors.temperature_celsius)
        """
        device_info = DeviceInfoModel(
            ip=data.get("ip", ""),
            firmware_version=data.get("fw_ver", ""),
            firmware_note=data.get("fw_note", ""),
            version=data.get("vr", 0),
            model=data.get("modello", 0),
            base_top=data.get("BaseTop", 0),
            grid_datamatrix=data.get("Grd_DM", ""),
            config_mode=data.get("config_mod", 0),
            slave_id=data.get("id_slave", 0),
            name=data.get("name", ""),
            has_slave=data.get("has_slave", 0),
            slave_bitmap=data.get("bmp_slave", 0)
        )

        sensors = SensorReadingsModel(
            temperature=data.get("v_tmpr", 0.0),
            humidity=data.get("v_umd", 0.0),
            air_quality=data.get("v_AirQ", 0),
            tvoc=data.get("v_Tvoc", 0),
            eco2=data.get("v_ECo2", 0),
            humidity_raw=data.get("umd_raw", 0),
            humidity_setpoint=TargetHumidityEnum(data.get("s_umd", 0)),
            co2_setpoint=data.get("s_co2", 0)
        )

        parameters = ParameterArraysModel(
            realtime=data.get("par_rt", []),
            minmax=data.get("par_mm", []),
            ambient=data.get("par_amb", []),
            external=data.get("par_ext", []),
            errors=data.get("err", []),
            manual=data.get("man", [])
        )

        operating = OperatingParametersModel(
            mode=DeviceModeEnum(data.get("mod", 1)),
            step_mode=data.get("step_mod", 0),
            on_off=OnOffStateEnum(data.get("on_off", 0)),
            speed=data.get("speed", 0),
            speed_requested=data.get("spd_rich", 0),
            speed_row=data.get("spd_row", 0),
            fan_direction=data.get("fan_dir", 0),
            direction=data.get("verso", 0),
            delta_temp_cycle=data.get("Delta_tmprCiclo", 0),
            delta_humidity_cycle=data.get("Delta_umdCiclo", 0),
            night_mode=data.get("night_mod", 0),
            led_on_off=data.get("led_on_off", 0),
            led_on_off_short=data.get("led_on_off_breve", 0),
            led_color=data.get("led_color", 0),
            chrono_mode=data.get("m_crono", 0),
            timer_active=data.get("tw_active", 0)
        )

        system = SystemInfoModel(
            counter=data.get("cntr", 0),
            memory_free=data.get("memfree", 0),
            uptime=data.get("up_time", 0),
            date=data.get("date", ""),
            time=data.get("time", ""),
            week=data.get("week", -1)
        )

        return cls(
            idp=data.get("idp", 0),
            frame_from=data.get("frm", ""),
            command=data.get("cmd", ""),
            response=data.get("res", 0),
            device_info=device_info,
            sensors=sensors,
            parameters=parameters,
            operating=operating,
            system=system,
            raw_data=data
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format."""
        return self.raw_data.copy()

    @property
    def is_healthy(self) -> bool:
        """Check if device is in healthy state."""
        return (
                self.response == 1 and
                not self.parameters.has_errors and
                self.system.memory_free > 10000
        )

    @property
    def is_on(self) -> bool:
        """Check if device is currently ON"""
        return self.operating.is_on

    @property
    def support_fan_speed_control(self) -> bool:
        """Check if device supports fan speed control"""
        return self.operating.mode in MODULAR_FAN_SPEED_PRESET_MODES

    @property
    def support_target_humidity_selection(self) -> bool:
        """Check if device supports target humidity selection"""
        return self.operating.mode in HUMIDITY_SELECTOR_PRESET_MODES

    @property
    def support_night_mode_toggle(self) -> bool:
        """Check if device supports night mode toggle"""
        return self.operating.mode in MODULAR_FAN_SPEED_PRESET_MODES