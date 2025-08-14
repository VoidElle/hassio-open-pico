from dataclasses import dataclass
from typing import Dict, Any, List
import json

from ..common.common_plant_model import CommonPlantModel


@dataclass(frozen=True)
class ResponseUserModel:
    """
    Attributes:
        res_code: Response code indicating status
        id: Id of the user
        token: The current session token (Needs to get worked to use in the next request)
        plants: The list of plants the user has
    """
    res_code: int
    id: int
    token: str
    plants: List[CommonPlantModel]

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'ResponseUserModel':
        """
        Create ResponseUserModel instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            ResponseUserModel instance
        """
        return cls(
            res_code=json_data['ResCode'],
            id=json_data['ID'],
            token=json_data['Token'],
            plants=[CommonPlantModel.from_json(d) for d in json_data.get("ListPlants", [])]
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert ResponseUserModel instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            'ResCode': self.res_code,
            'ID': self.id,
            'Token': self.token,
            'ListPlants': [d.to_json() for d in self.plants]
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'ResponseUserModel':
        """
        Create ResponseUserModel instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            ResponseUserModel instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert ResponseUserModel instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'ResponseUserModel':
        """
        Create a new instance with some fields replaced.

        Args:
            **kwargs: Fields to update (res_code, res_descr)

        Returns:
            New ResponseUserModel instance with updated fields
        """
        current_values = {
            'res_code': self.res_code,
            'id': self.id,
            'token': self.token,
            'plants': self.plants
        }
        current_values.update(kwargs)
        return ResponseUserModel(**current_values)