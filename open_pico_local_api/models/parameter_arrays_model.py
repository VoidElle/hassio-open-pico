from dataclasses import dataclass
from typing import List


@dataclass
class ParameterArraysModel:
    """Device parameter arrays"""
    realtime: List[int]  # par_rt
    minmax: List[int]  # par_mm
    ambient: List[int]  # par_amb
    external: List[int]  # par_ext
    errors: List[List[int]]  # err
    manual: List[int]  # man

    @property
    def has_errors(self) -> bool:
        """Check if device has any errors."""
        return any(len(err_list) > 0 for err_list in self.errors)

    @property
    def active_errors(self) -> List[int]:
        """Get all active error codes."""
        errors = []
        for err_list in self.errors:
            errors.extend(err_list)
        return errors