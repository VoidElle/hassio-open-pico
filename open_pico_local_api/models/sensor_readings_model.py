from dataclasses import dataclass

from ..enums.target_humidity_enum import TargetHumidityEnum


@dataclass
class SensorReadingsModel:
    """Real-time sensor readings"""
    temperature: float  # v_tmpr
    humidity: float  # v_umd
    air_quality: int  # v_AirQ
    tvoc: int  # v_Tvoc (Total Volatile Organic Compounds)
    eco2: int  # v_ECo2 (Equivalent CO2)

    # Raw values
    humidity_raw: int  # umd_raw

    # Setpoints
    humidity_setpoint: TargetHumidityEnum  # s_umd
    co2_setpoint: int  # s_co2

    @property
    def temperature_celsius(self) -> float:
        """Temperature in Celsius"""
        return round(self.temperature, 1)

    @property
    def humidity_percent(self) -> float:
        """Humidity as percentage"""
        return round(self.humidity, 1)

    @property
    def has_air_quality(self) -> bool:
        """Check if air quality sensor is available"""
        return self.air_quality > 0 or self.tvoc > 0 or self.eco2 > 0