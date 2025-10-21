from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass(frozen=True)
class CommonDeviceDetailsModel:
    """
    Attributes:
        serial: The device's serial (Injected, not given by API)
        speed_row: A percentage (0-100) that defines the current device's speed
        night_mode: Specify if the device's speed is in nith mode or not (1 yes - 2 no)
        led_on_off: Specify if the LED of the device is visible or not (0 no - 1 yes)
        s_umd: The selected target humidity (1 -> 40%, 2 -> 50%, 3 -> 60%)
    """
    serial: str
    speed_row: int
    speed_rich: int
    night_mode: int
    led_on_off: int
    s_umd: int

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'CommonDeviceDetailsModel':
        """
        Create CommonDeviceDetailsModel instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            CommonDeviceDetailsModel instance
        """
        return cls(
            serial=json_data['Serial'],
            speed_row=json_data['spd_row'],
            speed_rich=json_data['spd_rich'],
            night_mode=json_data['night_mod'],
            led_on_off=json_data['led_on_off'],
            s_umd=json_data['s_umd'],
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert CommonDeviceDetailsModel instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            'Serial': self.serial,
            'spd_row': self.speed_row,
            'spd_rich': self.speed_rich,
            'night_mod': self.night_mode,
            'led_on_off': self.led_on_off,
            's_umd': self.s_umd,
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'CommonDeviceDetailsModel':
        """
        Create CommonDeviceDetailsModel instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            CommonDeviceDetailsModel instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert CommonDeviceDetailsModel instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'CommonDeviceDetailsModel':
        """
        Create a new instance with some fields replaced.

        Args:
            **kwargs: Fields to update (res_code, res_descr)

        Returns:
            New CommonDeviceDetailsModel instance with updated fields
        """
        current_values = {
            'serial': self.serial,
            'speed_row': self.speed_row,
            'speed_rich': self.speed_rich,
            'night_mode': self.night_mode,
            'led_on_off': self.led_on_off,
            's_umd': self.s_umd,
        }
        current_values.update(kwargs)
        return CommonDeviceDetailsModel(**current_values)