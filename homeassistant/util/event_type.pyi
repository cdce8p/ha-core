"""Stub file for event_type. Provide overload for type checking."""
# ruff: noqa: PYI021  # Allow docstrings

from collections.abc import Mapping
from typing import Any

__all__ = [
    "EventType",
]

class EventType[_DataT: Mapping[str, Any] = Mapping[str, Any]]:
    """Custom type for Event.event_type. At runtime delegated to str.

    For type checkers pretend to be its own separate class.
    """

    def __init__(self, value: str, /) -> None: ...
    def __len__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __eq__(self, value: object, /) -> bool: ...
    def __getitem__(self, index: int) -> str: ...
