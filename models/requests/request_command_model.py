from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass(frozen=True)
class RequestCommandModel:
    """
    Attributes:
        command: The command that will be sent
        device_name: The device's name
        pin: The device's PIN
        serial: The device's serial
    """
    command: dict[str, str]
    device_name: str
    pin: str
    serial: str

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'RequestCommandModel':
        """
        Create RequestCommandModel instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            RequestCommandModel instance
        """
        return cls(
            command=json_data['Cmd'],
            device_name=json_data['Name'],
            pin=json_data['Pin'],
            serial=json_data['Serial'],
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert RequestCommandModel instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            "Cmd": self.command,
            "Name": self.device_name,
            "Pin": self.pin,
            "Serial": self.serial,
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'RequestCommandModel':
        """
        Create RequestCommandModel instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            RequestCommandModel instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert RequestCommandModel instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'RequestCommandModel':
        """
        Create a new instance with some fields replaced.

        Args:
            **kwargs: Fields to update

        Returns:
            New RequestCommandModel instance with updated fields
        """
        current_values = {
            'command': self.command,
            'device_name': self.device_name,
            'pin': self.pin,
            'serial': self.serial,
        }
        current_values.update(kwargs)
        return RequestCommandModel(**current_values)