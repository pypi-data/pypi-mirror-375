"""Functions for flattening nested data structures into key-value pairs."""

from typing import Any, overload

from bear_dereth.constants.typing_tools import LitFalse, LitTrue


@overload
def flatten(data: dict[str, Any], prefix: str, combine: LitTrue) -> str: ...
@overload
def flatten(data: dict[str, Any], prefix: str, combine: LitFalse = False) -> list[str]: ...
@overload
def flatten(data: list[Any], prefix: str, combine: LitTrue) -> str: ...
@overload
def flatten(data: list[Any], prefix: str, combine: LitFalse = False) -> list[str]: ...


def flatten(data: dict[str, Any] | list[Any], prefix: str = "", combine: bool = False) -> list[str] | str:
    """Convert JSON to simple key: value text format"""
    lines: list[str] = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix: str = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict | list)):
                lines.extend(flatten(value, new_prefix))
            else:
                lines.append(f"{new_prefix}: {value}")

    if isinstance(data, list):
        for i, item in enumerate(data):
            new_prefix = f"{prefix}[{i}]" if prefix else f"[{i}]"
            lines.extend(flatten(item, new_prefix))
    if combine:
        return "\n".join(lines)
    return lines
