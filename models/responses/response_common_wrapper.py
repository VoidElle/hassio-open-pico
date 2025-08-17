from dataclasses import dataclass
from typing import Dict, Any
import json


@dataclass(frozen=True)
class ResponseCommonResponseWrapper:
    """
    Attributes:
        res_code: Response code indicating status
        res_descr: Response description or message
    """
    res_code: int
    res_descr: str

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'ResponseCommonResponseWrapper':
        """
        Create ResponseCommonResponseWrapper instance from JSON dictionary.

        Args:
            json_data: Dictionary containing the JSON data

        Returns:
            ResponseCommonResponseWrapper instance
        """
        return cls(
            res_code=json_data['ResCode'],
            res_descr=json_data['ResDescr']
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert ResponseCommonResponseWrapper instance to JSON dictionary.

        Returns:
            Dictionary with JSON-serializable data
        """
        return {
            'ResCode': self.res_code,
            'ResDescr': self.res_descr
        }

    @classmethod
    def from_json_string(cls, json_string: str) -> 'ResponseCommonResponseWrapper':
        """
        Create ResponseCommonResponseWrapper instance from JSON string.

        Args:
            json_string: JSON string representation

        Returns:
            ResponseCommonResponseWrapper instance
        """
        return cls.from_json(json.loads(json_string))

    def to_json_string(self) -> str:
        """
        Convert ResponseCommonResponseWrapper instance to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def copy_with(self, **kwargs) -> 'ResponseCommonResponseWrapper':
        """
        Create a new instance with some fields replaced.

        Args:
            **kwargs: Fields to update (res_code, res_descr)

        Returns:
            New ResponseCommonResponseWrapper instance with updated fields
        """
        current_values = {
            'res_code': self.res_code,
            'res_descr': self.res_descr
        }
        current_values.update(kwargs)
        return ResponseCommonResponseWrapper(**current_values)