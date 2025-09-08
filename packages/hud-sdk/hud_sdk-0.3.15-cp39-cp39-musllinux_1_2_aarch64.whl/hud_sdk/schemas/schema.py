from abc import ABC
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    TypeVar,
    Union,
)

JSON = Union[
    str, int, float, bool, Dict["JSON", "JSON"], List["JSON"], "Schema", Enum, None
]

JSONType = TypeVar("JSONType", bound=JSON)
JSONTypeKey = TypeVar("JSONTypeKey", bound=JSON)
JSONTypeValue = TypeVar("JSONTypeValue", bound=JSON)


class Schema(ABC):
    def to_dict(self) -> Dict[str, Any]:
        """Create dictionary directly for maximum efficiency"""
        raise NotImplementedError("Subclasses must implement to_dict()")
