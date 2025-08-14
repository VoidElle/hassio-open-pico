from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass(frozen=True)
class RequestLoginModel:
    """
    Attributes:
        device_id: Device identifier
        platform: Platform information
        password: User password
        token_push: Push notification token
        username: Username for login
    """
    device_id: str
    platform: str
    password: str
    token_push: str
    username: str

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'RequestLoginModel':
        """
        Create RequestLoginModel instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            RequestLoginModel instance
        """
        return cls(
            device_id=json_data['DeviceId'],
            platform=json_data['Platform'],
            password=json_data['Password'],
            token_push=json_data['TokenPush'],
            username=json_data['Username']
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert RequestLoginModel instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            'DeviceId': self.device_id,
            'Platform': self.platform,
            'Password': self.password,
            'TokenPush': self.token_push,
            'Username': self.username
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'RequestLoginModel':
        """
        Create RequestLoginModel instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            RequestLoginModel instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert RequestLoginModel instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'RequestLoginModel':
        """
        Create a new instance with some fields replaced.
        Similar to Dart's copyWith method.

        Args:
            **kwargs: Fields to update

        Returns:
            New RequestLoginModel instance with updated fields
        """
        current_values = {
            'device_id': self.device_id,
            'platform': self.platform,
            'password': self.password,
            'token_push': self.token_push,
            'username': self.username
        }
        current_values.update(kwargs)
        return RequestLoginModel(**current_values)