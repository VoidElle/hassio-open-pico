from dataclasses import dataclass
from typing import Dict, Any, List
import json

from .common_device_model import CommonDeviceModel


@dataclass(frozen=True)
class CommonPlantModel:
    """
    Attributes:
        id: ID of the plant
        name: Name of the plant
        usan_id: ID of the usan of the plant
        devices: List of the devices in the Plant
    """
    id: int
    name: str
    usan_id: int
    icon: int
    devices: List[CommonDeviceModel]

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'CommonPlantModel':
        """
        Create CommonPlantModel instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            CommonPlantModel instance
        """
        return cls(
            id=json_data['LVPL_Id'],
            name=json_data['LVPL_Name'],
            usan_id=json_data['LVPL_USAN_Id'],
            icon=json_data['LVPL_Icon'],
            devices=[CommonDeviceModel.from_json(d) for d in json_data.get("ListDevices", [])]
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert CommonPlantModel instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            'LVPL_Id': self.id,
            'LVPL_Name': self.name,
            'LVPL_USAN_Id': self.usan_id,
            'LVPL_Icon': self.icon,
            'Devices': [d.to_json() for d in self.devices]
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'CommonPlantModel':
        """
        Create CommonPlantModel instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            CommonPlantModel instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert CommonPlantModel instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'CommonPlantModel':
        """
        Create a new instance with some fields replaced.

        Args:
            **kwargs: Fields to update (res_code, res_descr)

        Returns:
            New CommonPlantModel instance with updated fields
        """
        current_values = {
            'id': self.id,
            'name': self.name,
            'usan_id': self.usan_id,
            'icon': self.icon,
            'devices': self.devices
        }
        current_values.update(kwargs)
        return CommonPlantModel(**current_values)