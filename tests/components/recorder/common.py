"""Common test utils for working with recorder."""
import asyncio
from datetime import timedelta

from homeassistant import core as ha
from homeassistant.components import recorder
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import dt as dt_util

from tests.common import async_fire_time_changed, fire_time_changed


def wait_recording_done(hass):
    """Block till recording is done."""
    trigger_db_commit(hass)
    hass.block_till_done()
    hass.data[recorder.DATA_INSTANCE].block_till_done()
    hass.block_till_done()


def trigger_db_commit(hass):
    """Force the recorder to commit."""
    for _ in range(recorder.DEFAULT_COMMIT_INTERVAL):
        # We only commit on time change
        fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))


async def async_wait_recording_done(
    hass: HomeAssistantType,
    instance: recorder.Recorder,
) -> None:
    """Async wait until recording is done."""
    async_trigger_db_commit(hass)
    await hass.async_block_till_done()
    await async_recorder_block_till_done(instance)
    await hass.async_block_till_done()


@ha.callback
def async_trigger_db_commit(hass: HomeAssistantType) -> None:
    """Fore the recorder to commit. Async friendly."""
    for _ in range(recorder.DEFAULT_COMMIT_INTERVAL):
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=1))


async def async_recorder_block_till_done(instance: recorder.Recorder) -> None:
    """Non blocking version of recorder.block_till_done()."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, instance.block_till_done)
