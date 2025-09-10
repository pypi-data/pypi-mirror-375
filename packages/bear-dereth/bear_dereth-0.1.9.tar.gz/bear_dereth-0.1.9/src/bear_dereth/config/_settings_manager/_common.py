from collections.abc import Callable, Mapping
from types import NoneType
from typing import Literal

TypeList = Literal["string", "number", "float", "list", "boolean", "null"]
"""A type alias for the allowed types in settings."""

ValueType = str | int | float | list | bool | NoneType
"""A type alias for the allowed value types in settings."""

PossibleTypes = type[bool] | type[int] | type[float] | type[str] | type[NoneType] | type[list]
"""A type alias for the possible Python types corresponding to ValueType."""

QueryCheck = Callable[[Mapping], bool]
"""A type alias for a callable that checks a settings record."""

OpType = Literal["path", "==", "!=", ">", "<", ">=", "<=", "exists", "and", "or", "not", "matches", "all", "search"]
"""A type alias for the supported query operation types."""
