"""Helper to help coordinating calls."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
import functools
from typing import Any, Literal, cast, overload

from homeassistant.core import HomeAssistant
from homeassistant.loader import bind_hass
from homeassistant.util.hass_dict import HassKey

type _FuncType[_T] = Callable[[HomeAssistant], _T]
type _Coro[_T] = Coroutine[Any, Any, _T]


@overload
def singleton[_T](
    data_key: HassKey[_T], *, async_: Literal[True]
) -> Callable[[_FuncType[_Coro[_T]]], _FuncType[_Coro[_T]]]: ...


@overload
def singleton[_T](
    data_key: HassKey[_T],
) -> Callable[[_FuncType[_T]], _FuncType[_T]]: ...


@overload
def singleton[_T](data_key: str) -> Callable[[_FuncType[_T]], _FuncType[_T]]: ...


def singleton[_T](
    data_key: Any, *, async_: bool = False
) -> Callable[[_FuncType[_T]], _FuncType[_T]]:
    """Decorate a function that should be called once per instance.

    Result will be cached and simultaneous calls will be handled.
    """

    @overload
    def wrapper(func: _FuncType[_Coro[_T]]) -> _FuncType[_Coro[_T]]: ...

    @overload
    def wrapper(func: _FuncType[_T]) -> _FuncType[_T]: ...

    def wrapper(func: _FuncType[_Coro[_T] | _T]) -> _FuncType[_Coro[_T] | _T]:  # type: ignore[misc]
        """Wrap a function with caching logic."""
        if not asyncio.iscoroutinefunction(func):

            @functools.lru_cache(maxsize=1)
            @bind_hass
            @functools.wraps(func)
            def wrapped(hass: HomeAssistant) -> _T:
                if data_key not in hass.data:
                    hass.data[data_key] = func(hass)
                return cast(_T, hass.data[data_key])

            return wrapped

        @bind_hass
        @functools.wraps(func)
        async def async_wrapped(hass: HomeAssistant) -> _T:
            if data_key not in hass.data:
                evt = hass.data[data_key] = asyncio.Event()
                result = await func(hass)
                hass.data[data_key] = result
                evt.set()
                return cast(_T, result)

            obj_or_evt = hass.data[data_key]

            if isinstance(obj_or_evt, asyncio.Event):
                await obj_or_evt.wait()
                return cast(_T, hass.data[data_key])

            return cast(_T, obj_or_evt)

        return async_wrapped

    return wrapper
