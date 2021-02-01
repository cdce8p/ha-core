"""Test data purging."""
from datetime import datetime, timedelta
import json
from typing import Any
from unittest.mock import patch

from sqlalchemy.orm.session import Session

from homeassistant.components import recorder
from homeassistant.components.recorder.const import DATA_INSTANCE
from homeassistant.components.recorder.models import Events, RecorderRuns, States
from homeassistant.components.recorder.purge import _purge_filtered_data, purge_old_data
from homeassistant.components.recorder.util import session_scope
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.util import dt as dt_util

from tests.components.recorder.common import (
    async_recorder_block_till_done,
    async_wait_recording_done,
    wait_recording_done,
)
from tests.components.recorder.conftest import SetupRecorderInstanceT

MODULE_PATH = "homeassistant.components.recorder.purge"


def test_purge_old_states(hass, hass_recorder):
    """Test deleting old states."""
    hass = hass_recorder()
    _add_test_states(hass)

    # make sure we start with 6 states
    with session_scope(hass=hass) as session:
        states = session.query(States)
        assert states.count() == 6

        # run purge_old_data()
        finished = purge_old_data(hass.data[DATA_INSTANCE], 4, repack=False)
        assert not finished
        assert states.count() == 4

        finished = purge_old_data(hass.data[DATA_INSTANCE], 4, repack=False)
        assert not finished
        assert states.count() == 2

        finished = purge_old_data(hass.data[DATA_INSTANCE], 4, repack=False)
        assert finished
        assert states.count() == 2


def test_purge_old_events(hass, hass_recorder):
    """Test deleting old events."""
    hass = hass_recorder()
    _add_test_events(hass)

    with session_scope(hass=hass) as session:
        events = session.query(Events).filter(Events.event_type.like("EVENT_TEST%"))
        assert events.count() == 6

        # run purge_old_data()
        finished = purge_old_data(hass.data[DATA_INSTANCE], 4, repack=False)
        assert not finished
        assert events.count() == 4

        finished = purge_old_data(hass.data[DATA_INSTANCE], 4, repack=False)
        assert not finished
        assert events.count() == 2

        # we should only have 2 events left
        finished = purge_old_data(hass.data[DATA_INSTANCE], 4, repack=False)
        assert finished
        assert events.count() == 2


def test_purge_old_recorder_runs(hass, hass_recorder):
    """Test deleting old recorder runs keeps current run."""
    hass = hass_recorder()
    _add_test_recorder_runs(hass)

    # make sure we start with 7 recorder runs
    with session_scope(hass=hass) as session:
        recorder_runs = session.query(RecorderRuns)
        assert recorder_runs.count() == 7

        # run purge_old_data()
        finished = purge_old_data(hass.data[DATA_INSTANCE], 0, repack=False)
        assert finished
        assert recorder_runs.count() == 1


def test_purge_method(hass, hass_recorder):
    """Test purge method."""
    hass = hass_recorder()
    service_data = {"keep_days": 4}
    _add_test_events(hass)
    _add_test_states(hass)
    _add_test_recorder_runs(hass)

    # make sure we start with 6 states
    with session_scope(hass=hass) as session:
        states = session.query(States)
        assert states.count() == 6

        events = session.query(Events).filter(Events.event_type.like("EVENT_TEST%"))
        assert events.count() == 6

        recorder_runs = session.query(RecorderRuns)
        assert recorder_runs.count() == 7

        hass.data[DATA_INSTANCE].block_till_done()
        wait_recording_done(hass)

        # run purge method - no service data, use defaults
        hass.services.call("recorder", "purge")
        hass.block_till_done()

        # Small wait for recorder thread
        hass.data[DATA_INSTANCE].block_till_done()
        wait_recording_done(hass)

        # only purged old events
        assert states.count() == 4
        assert events.count() == 4

        # run purge method - correct service data
        hass.services.call("recorder", "purge", service_data=service_data)
        hass.block_till_done()

        # Small wait for recorder thread
        hass.data[DATA_INSTANCE].block_till_done()
        wait_recording_done(hass)

        # we should only have 2 states left after purging
        assert states.count() == 2

        # now we should only have 2 events left
        assert events.count() == 2

        # now we should only have 3 recorder runs left
        assert recorder_runs.count() == 3

        assert not ("EVENT_TEST_PURGE" in (event.event_type for event in events.all()))

        # run purge method - correct service data, with repack
        with patch("homeassistant.components.recorder.purge._LOGGER") as mock_logger:
            service_data["repack"] = True
            hass.services.call("recorder", "purge", service_data=service_data)
            hass.block_till_done()
            hass.data[DATA_INSTANCE].block_till_done()
            wait_recording_done(hass)
            assert (
                mock_logger.debug.mock_calls[2][1][0]
                == "Vacuuming SQL DB to free space"
            )


async def test_purge_edge_case(
    hass: HomeAssistantType,
    async_setup_recorder_instance: SetupRecorderInstanceT,
):
    """Test states and events are purged even if they occurred shortly before purge_before."""

    async def _add_test_state(hass: HomeAssistantType, timestamp: datetime) -> None:
        with recorder.session_scope(hass=hass) as session:
            session.add(
                States(
                    entity_id="test.recorder2",
                    domain="sensor",
                    state="purgeme",
                    attributes="{}",
                    last_changed=timestamp,
                    last_updated=timestamp,
                    created=timestamp,
                    event_id=1001,
                )
            )

    async def _add_test_event(hass: HomeAssistantType, timestamp: datetime) -> None:
        with recorder.session_scope(hass=hass) as session:
            session.add(
                Events(
                    event_type="EVENT_TEST_PURGE",
                    event_data="{}",
                    origin="LOCAL",
                    created=timestamp,
                    time_fired=timestamp,
                )
            )

    instance = await async_setup_recorder_instance(hass, None)
    await async_wait_recording_done(hass, instance)

    service_data = {"keep_days": 2}
    timestamp = dt_util.utcnow() - timedelta(days=2, minutes=1)

    # Test with state
    await _add_test_state(hass, timestamp)
    with session_scope(hass=hass) as session:
        states = session.query(States)
        assert states.count() == 1

        await hass.services.async_call(
            recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
        )
        await hass.async_block_till_done()

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        assert states.count() == 0

    # Test with event
    await _add_test_event(hass, timestamp)
    with session_scope(hass=hass) as session:
        events = session.query(Events).filter(Events.event_type == "EVENT_TEST_PURGE")
        assert events.count() == 1

        await hass.services.async_call(
            recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
        )
        await hass.async_block_till_done()

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        assert events.count() == 0


async def test_purge_filtered_states(
    hass: HomeAssistantType,
    async_setup_recorder_instance: SetupRecorderInstanceT,
):
    """Test filtered states are purged."""
    config: ConfigType = {"exclude": {"entities": ["sensor.excluded"]}}
    instance = await async_setup_recorder_instance(hass, config)
    assert instance.entity_filter("sensor.excluded") is False

    def _add_db_entries(hass: HomeAssistantType) -> None:
        with recorder.session_scope(hass=hass) as session:
            # Add states and state_changed events that should be purged
            for days in range(1, 4):
                timestamp = dt_util.utcnow() - timedelta(days=days)
                for event_id in range(1000, 1020):
                    _add_state_and_state_changed_event(
                        session,
                        "sensor.excluded",
                        "purgeme",
                        timestamp,
                        event_id * days,
                    )
            # Add states and state_changed events that should be keeped
            timestamp = dt_util.utcnow() - timedelta(days=2)
            for event_id in range(200, 210):
                _add_state_and_state_changed_event(
                    session,
                    "sensor.keep",
                    "keep",
                    timestamp,
                    event_id,
                )
            # Add event that should be keeped
            session.add(
                Events(
                    event_id=100,
                    event_type="EVENT_KEEP",
                    event_data="{}",
                    origin="LOCAL",
                    created=timestamp,
                    time_fired=timestamp,
                )
            )

    def _mocked_purge_filtered_data(*args: Any, **kwargs: Any) -> bool:
        kwargs["subset_size"] = 5
        return _purge_filtered_data(*args, **kwargs)

    service_data = {"keep_days": 10}
    _add_db_entries(hass)

    with session_scope(hass=hass) as session:
        states = session.query(States)
        assert states.count() == 70

        events_state_changed = session.query(Events).filter(
            Events.event_type == EVENT_STATE_CHANGED
        )
        events_keep = session.query(Events).filter(Events.event_type == "EVENT_KEEP")
        assert events_state_changed.count() == 70
        assert events_keep.count() == 1

        # Normal purge doesn't remove excluded entities
        await hass.services.async_call(
            recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
        )
        await hass.async_block_till_done()

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        assert states.count() == 70
        assert events_state_changed.count() == 70
        assert events_keep.count() == 1

        # Test with 'apply_filter' = True
        with patch(
            f"{MODULE_PATH}._purge_filtered_data",
            side_effect=_mocked_purge_filtered_data,
        ):
            service_data["apply_filter"] = True
            await hass.services.async_call(
                recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
            )
            await hass.async_block_till_done()

            await async_recorder_block_till_done(instance)
            await async_wait_recording_done(hass, instance)

            await async_recorder_block_till_done(instance)
            await async_wait_recording_done(hass, instance)

        assert states.count() == 10
        assert events_state_changed.count() == 10
        assert events_keep.count() == 1

        states_sensor_excluded = session.query(States).filter(
            States.entity_id == "sensor.excluded"
        )
        assert states_sensor_excluded.count() == 0


async def test_purge_filtered_events(
    hass: HomeAssistantType,
    async_setup_recorder_instance: SetupRecorderInstanceT,
):
    """Test filtered events are purged."""
    config: ConfigType = {"exclude": {"event_types": ["EVENT_PURGE"]}}
    instance = await async_setup_recorder_instance(hass, config)

    def _add_db_entries(hass: HomeAssistantType) -> None:
        with recorder.session_scope(hass=hass) as session:
            # Add events that should be purged
            for days in range(1, 4):
                timestamp = dt_util.utcnow() - timedelta(days=days)
                for event_id in range(1000, 1020):
                    session.add(
                        Events(
                            event_id=event_id * days,
                            event_type="EVENT_PURGE",
                            event_data="{}",
                            origin="LOCAL",
                            created=timestamp,
                            time_fired=timestamp,
                        )
                    )

            # Add states and state_changed events that should be keeped
            timestamp = dt_util.utcnow() - timedelta(days=1)
            for event_id in range(200, 210):
                _add_state_and_state_changed_event(
                    session,
                    "sensor.keep",
                    "keep",
                    timestamp,
                    event_id,
                )

    service_data = {"keep_days": 10}
    _add_db_entries(hass)

    with session_scope(hass=hass) as session:
        events_purge = session.query(Events).filter(Events.event_type == "EVENT_PURGE")
        events_keep = session.query(Events).filter(
            Events.event_type == EVENT_STATE_CHANGED
        )
        states = session.query(States)

        assert events_purge.count() == 60
        assert events_keep.count() == 10
        assert states.count() == 10

        # Normal purge doesn't remove excluded events
        await hass.services.async_call(
            recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
        )
        await hass.async_block_till_done()

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        assert events_purge.count() == 60
        assert events_keep.count() == 10
        assert states.count() == 10

        # Test with 'apply_filter' = True
        service_data["apply_filter"] = True
        await hass.services.async_call(
            recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
        )
        await hass.async_block_till_done()

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        assert events_purge.count() == 0
        assert events_keep.count() == 10
        assert states.count() == 10


async def test_purge_filtered_events_state_changed(
    hass: HomeAssistantType,
    async_setup_recorder_instance: SetupRecorderInstanceT,
):
    """Test filtered state_changed events are purged. This should also remove all states."""
    config: ConfigType = {"exclude": {"event_types": [EVENT_STATE_CHANGED]}}
    instance = await async_setup_recorder_instance(hass, config)
    # Assert entity_id is NOT excluded
    assert instance.entity_filter("sensor.excluded") is True

    def _add_db_entries(hass: HomeAssistantType) -> None:
        with recorder.session_scope(hass=hass) as session:
            # Add states and state_changed events that should be purged
            for days in range(1, 4):
                timestamp = dt_util.utcnow() - timedelta(days=days)
                for event_id in range(1000, 1020):
                    _add_state_and_state_changed_event(
                        session,
                        "sensor.excluded",
                        "purgeme",
                        timestamp,
                        event_id * days,
                    )
            # Add events that should be keeped
            timestamp = dt_util.utcnow() - timedelta(days=1)
            for event_id in range(200, 210):
                session.add(
                    Events(
                        event_id=event_id,
                        event_type="EVENT_KEEP",
                        event_data="{}",
                        origin="LOCAL",
                        created=timestamp,
                        time_fired=timestamp,
                    )
                )

    service_data = {"keep_days": 10, "apply_filter": True}
    _add_db_entries(hass)

    with session_scope(hass=hass) as session:
        events_keep = session.query(Events).filter(Events.event_type == "EVENT_KEEP")
        events_purge = session.query(Events).filter(
            Events.event_type == EVENT_STATE_CHANGED
        )
        states = session.query(States)

        assert events_keep.count() == 10
        assert events_purge.count() == 60
        assert states.count() == 60

        await hass.services.async_call(
            recorder.DOMAIN, recorder.SERVICE_PURGE, service_data
        )
        await hass.async_block_till_done()

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        await async_recorder_block_till_done(instance)
        await async_wait_recording_done(hass, instance)

        assert events_keep.count() == 10
        assert events_purge.count() == 0
        assert states.count() == 0


def _add_test_states(hass):
    """Add multiple states to the db for testing."""
    now = datetime.now()
    five_days_ago = now - timedelta(days=5)
    eleven_days_ago = now - timedelta(days=11)
    attributes = {"test_attr": 5, "test_attr_10": "nice"}

    hass.block_till_done()
    hass.data[DATA_INSTANCE].block_till_done()
    wait_recording_done(hass)

    with recorder.session_scope(hass=hass) as session:
        for event_id in range(6):
            if event_id < 2:
                timestamp = eleven_days_ago
                state = "autopurgeme"
            elif event_id < 4:
                timestamp = five_days_ago
                state = "purgeme"
            else:
                timestamp = now
                state = "dontpurgeme"

            session.add(
                States(
                    entity_id="test.recorder2",
                    domain="sensor",
                    state=state,
                    attributes=json.dumps(attributes),
                    last_changed=timestamp,
                    last_updated=timestamp,
                    created=timestamp,
                    event_id=event_id + 1000,
                )
            )


def _add_test_events(hass):
    """Add a few events for testing."""
    now = datetime.now()
    five_days_ago = now - timedelta(days=5)
    eleven_days_ago = now - timedelta(days=11)
    event_data = {"test_attr": 5, "test_attr_10": "nice"}

    hass.block_till_done()
    hass.data[DATA_INSTANCE].block_till_done()
    wait_recording_done(hass)

    with recorder.session_scope(hass=hass) as session:
        for event_id in range(6):
            if event_id < 2:
                timestamp = eleven_days_ago
                event_type = "EVENT_TEST_AUTOPURGE"
            elif event_id < 4:
                timestamp = five_days_ago
                event_type = "EVENT_TEST_PURGE"
            else:
                timestamp = now
                event_type = "EVENT_TEST"

            session.add(
                Events(
                    event_type=event_type,
                    event_data=json.dumps(event_data),
                    origin="LOCAL",
                    created=timestamp,
                    time_fired=timestamp,
                )
            )


def _add_test_recorder_runs(hass):
    """Add a few recorder_runs for testing."""
    now = dt_util.utcnow()
    five_days_ago = now - timedelta(days=5)
    eleven_days_ago = now - timedelta(days=11)

    hass.block_till_done()
    hass.data[DATA_INSTANCE].block_till_done()
    wait_recording_done(hass)

    with recorder.session_scope(hass=hass) as session:
        for rec_id in range(6):
            if rec_id < 2:
                timestamp = eleven_days_ago
            elif rec_id < 4:
                timestamp = five_days_ago
            else:
                timestamp = now

            session.add(
                RecorderRuns(
                    start=timestamp,
                    created=dt_util.utcnow(),
                    end=timestamp + timedelta(days=1),
                )
            )


def _add_state_and_state_changed_event(
    session: Session,
    entity_id: str,
    state: str,
    timestamp: datetime,
    event_id: int,
) -> None:
    """Add state and state_changed event to database for testing."""
    session.add(
        States(
            entity_id=entity_id,
            domain="sensor",
            state=state,
            attributes="{}",
            last_changed=timestamp,
            last_updated=timestamp,
            created=timestamp,
            event_id=event_id,
        )
    )
    session.add(
        Events(
            event_id=event_id,
            event_type=EVENT_STATE_CHANGED,
            event_data="{}",
            origin="LOCAL",
            created=timestamp,
            time_fired=timestamp,
        )
    )
