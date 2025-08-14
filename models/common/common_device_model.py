from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass(frozen=True)
class CommonDeviceModel:
    """
    Attributes:
        id: ID of the device
        serial: Serial of the device
        name: Name of the device
        operating_mode: The current operating mode of the device
        is_off: Whether the device is on or off
    """
    id: int
    serial: str
    name: str
    operating_mode: int
    is_off: bool

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'CommonDeviceModel':
        """
        Create CommonDeviceModel instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            CommonDeviceModel instance
        """
        return cls(
            id=json_data['DevId'],
            serial=json_data['Serial'],
            name=json_data['Name'],
            operating_mode=json_data['OperatingMode'],
            is_off=json_data['IsOff']
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert CommonDeviceModel instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            'DevId': self.id,
            'Serial': self.serial,
            'Name': self.name,
            'OperatingMode': self.operating_mode,
            'IsOff': self.is_off
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'CommonDeviceModel':
        """
        Create CommonDeviceModel instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            CommonDeviceModel instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert CommonDeviceModel instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'CommonDeviceModel':
        """
        Create a new instance with some fields replaced.

        Args:
            **kwargs: Fields to update (res_code, res_descr)

        Returns:
            New CommonDeviceModel instance with updated fields
        """
        current_values = {
            'id': self.id,
            'name': self.name,
            'serial': self.serial,
            'operating_mode': self.operating_mode,
            'is_off': self.is_off
        }
        current_values.update(kwargs)
        return CommonDeviceModel(**current_values)