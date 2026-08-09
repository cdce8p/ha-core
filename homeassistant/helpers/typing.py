"""Typing Helpers for Home Assistant."""

from collections.abc import Mapping
from typing import Any, Never

from typing_extensions import sentinel
import voluptuous as vol

type GPSType = tuple[float, float]
type ConfigType = dict[str, Any]
type DiscoveryInfoType = dict[str, Any]
type ServiceDataType = dict[str, Any]
type StateType = str | int | float | None
type TemplateVarsType = Mapping[str, Any] | None
type NoEventData = Mapping[str, Never]
type VolSchemaType = vol.Schema | vol.All | vol.Any
type VolDictType = dict[str | vol.Marker, Any]

# Custom type for recorder Queries
type QueryType = Any

Undefined = sentinel("Undefined")
