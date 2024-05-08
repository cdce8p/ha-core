"""Decorator utility functions."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from typing import Any

MYPY = 0

if MYPY:

    class Registry[_KT: Hashable, _VT: Callable[..., Any]](dict[_KT, _VT]):
        """Registry of items."""

        def register(self, name: _KT) -> Callable[[_VT], _VT]:  # TODO pyright
            """Return decorator to register item with a specific name."""

            def decorator(func: _VT) -> _VT:
                """Register decorated function."""
                self[name] = func
                return func

            return decorator
else:

    class Registry[_KT: Hashable, _VT: Callable[..., Any]](dict[_KT, _VT]):
        """Registry of items."""

        def register[_T: Callable[..., Any]](  # TODO pyright
            self, name: _KT
        ) -> Callable[[_T], _T]:
            """Return decorator to register item with a specific name."""

            def decorator(func: _T) -> _T:
                """Register decorated function."""
                self[name] = func
                return func

            return decorator
