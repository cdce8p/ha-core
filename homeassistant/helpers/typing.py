"""Typing Helpers for Home Assistant."""

from collections.abc import Mapping
from typing import Any, Never

import probatio
from typing_extensions import sentinel

type GPSType = tuple[float, float]
type ConfigType = dict[str, Any]
type DiscoveryInfoType = dict[str, Any]
type ServiceDataType = dict[str, Any]
type StateType = str | int | float | None
type TemplateVarsType = Mapping[str, Any] | None
type NoEventData = Mapping[str, Never]
type VolSchemaType = probatio.Schema | probatio.All | probatio.Any
type VolDictType = dict[str | probatio.Marker, Any]

# Custom type for recorder Queries
type QueryType = Any

Undefined = sentinel("Undefined")
