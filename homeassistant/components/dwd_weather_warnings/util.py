"""Util functions for the dwd_weather_warnings integration."""

from __future__ import annotations

from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .exceptions import EntityNotFoundError


def get_position_data(
    hass: HomeAssistant, registry_id: str
) -> tuple[float, float] | None:
    """Extract longitude and latitude from a device tracker."""
    registry = er.async_get(hass)
    if (registry_entry := registry.async_get(registry_id)) is None:
        raise EntityNotFoundError(f"Failed to find registry entry {registry_id}")

    if (entity := hass.states.get(registry_entry.entity_id)) is None:
        raise EntityNotFoundError(f"Failed to find entity {registry_entry.entity_id}")

    if not (latitude := entity.attributes.get(ATTR_LATITUDE)):
        raise AttributeError(
            f"Failed to find attribute '{ATTR_LATITUDE}' in {registry_entry.entity_id}",
            ATTR_LATITUDE,
        )

    if not (longitude := entity.attributes.get(ATTR_LONGITUDE)):
        raise AttributeError(
            f"Failed to find attribute '{ATTR_LONGITUDE}' in {registry_entry.entity_id}",
            ATTR_LONGITUDE,
        )

    return (latitude, longitude)
