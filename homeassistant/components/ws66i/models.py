"""The ws66i integration models."""

from __future__ import annotations

from dataclasses import dataclass
import sys

from .coordinator import Ws66iDataUpdateCoordinator

if sys.version_info < (3, 13):
    from pyws66i import WS66i


@dataclass
class SourceRep:
    """Different representations of the amp sources."""

    id_name: dict[int, str]
    name_id: dict[str, int]
    name_list: list[str]


@dataclass
class Ws66iData:
    """Data for the ws66i integration."""

    host_ip: str
    device: WS66i
    sources: SourceRep
    coordinator: Ws66iDataUpdateCoordinator
    zones: list[int]
