"""Comelit constants."""

import logging
import sys

if sys.version_info < (3, 13):
    from aiocomelit.const import BRIDGE, VEDO

_LOGGER = logging.getLogger(__package__)

DOMAIN = "comelit"
DEFAULT_PORT = 80
DEVICE_TYPE_LIST = [BRIDGE, VEDO]
