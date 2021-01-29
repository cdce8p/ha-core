"""Purge old data helper."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import time
from typing import TYPE_CHECKING, List

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import distinct

from homeassistant.const import EVENT_STATE_CHANGED
import homeassistant.util.dt as dt_util

from .models import Events, RecorderRuns, States
from .util import execute, session_scope

if TYPE_CHECKING:  # pragma: no cover
    from . import Recorder

_LOGGER = logging.getLogger(__name__)

DEBUG_DATETIME_FMT = r"%Y-%m-%d %H:%M UTC"


def purge_old_data(
    instance, purge_days: int, repack: bool, apply_filter: bool = False
) -> bool:
    """Purge events and states older than purge_days ago.

    Cleans up an timeframe of an hour, based on the oldest record.
    """
    purge_before = dt_util.utcnow() - timedelta(days=purge_days)
    _LOGGER.debug("Purging states and events before target %s", purge_before)

    try:
        with session_scope(session=instance.get_session()) as session:
            # Purge a max of 1 hour, based on the oldest states or events record
            batch_purge_before = purge_before
            purge_incomplete: bool = False

            query = session.query(States).order_by(States.last_updated.asc()).limit(1)
            states = execute(query, to_native=True, validate_entity_ids=False)
            if states and (last_updated := states[0].last_updated) < batch_purge_before:
                batch_purge_before = min(
                    batch_purge_before,
                    last_updated + timedelta(hours=1),
                )
                purge_incomplete = True

            query = session.query(Events).order_by(Events.time_fired.asc()).limit(1)
            events = execute(query, to_native=True)
            if events and (time_fired := events[0].time_fired) < batch_purge_before:
                batch_purge_before = min(
                    batch_purge_before,
                    time_fired + timedelta(hours=1),
                )
                purge_incomplete = True

            if purge_incomplete:
                _LOGGER.debug(
                    "Purging states and events before %s",
                    batch_purge_before.strftime(DEBUG_DATETIME_FMT),
                )

                deleted_rows = (
                    session.query(States)
                    .filter(States.last_updated < batch_purge_before)
                    .delete(synchronize_session=False)
                )
                _LOGGER.debug("Deleted %s states", deleted_rows)

                deleted_rows = (
                    session.query(Events)
                    .filter(Events.time_fired < batch_purge_before)
                    .delete(synchronize_session=False)
                )
                _LOGGER.debug("Deleted %s events", deleted_rows)

                # If states or events purging isn't processing the purge_before yet,
                # return false, as we are not done yet.
                if batch_purge_before != purge_before:
                    _LOGGER.debug("Purging hasn't fully completed yet")
                    return False

            if apply_filter:
                if _purge_filtered_data(instance, session) is False:
                    return False

            # Recorder runs is small, no need to batch run it
            deleted_rows = (
                session.query(RecorderRuns)
                .filter(RecorderRuns.start < purge_before)
                .filter(RecorderRuns.run_id != instance.run_info.run_id)
                .delete(synchronize_session=False)
            )
            _LOGGER.debug("Deleted %s recorder_runs", deleted_rows)

        if repack:
            # Execute sqlite or postgresql vacuum command to free up space on disk
            if instance.engine.driver in ("pysqlite", "postgresql"):
                _LOGGER.debug("Vacuuming SQL DB to free space")
                instance.engine.execute("VACUUM")
            # Optimize mysql / mariadb tables to free up space on disk
            elif instance.engine.driver in ("mysqldb", "pymysql"):
                _LOGGER.debug("Optimizing SQL DB to free space")
                instance.engine.execute("OPTIMIZE TABLE states, events, recorder_runs")

    except OperationalError as err:
        # Retry when one of the following MySQL errors occurred:
        # 1205: Lock wait timeout exceeded; try restarting transaction
        # 1206: The total number of locks exceeds the lock table size
        # 1213: Deadlock found when trying to get lock; try restarting transaction
        if instance.engine.driver in ("mysqldb", "pymysql") and err.orig.args[0] in (
            1205,
            1206,
            1213,
        ):
            _LOGGER.info("%s; purge not completed, retrying", err.orig.args[1])
            time.sleep(instance.db_retry_wait)
            return False

        _LOGGER.warning("Error purging history: %s", err)
    except SQLAlchemyError as err:
        _LOGGER.warning("Error purging history: %s", err)
    return True


def _purge_filtered_data(
    instance: Recorder,
    session: Session,
    *,
    batch_size_hours: int = 1,
    subset_size: int = 1000,
) -> bool:
    """Purge filtered states and events that shouldn't be in database."""

    _LOGGER.debug("Purging filtered states and events")
    utc_now = dt_util.utcnow()
    batch_purge_before_states = utc_now
    batch_purge_before_events = utc_now

    # Check if excluded entity_ids are in database
    excluded_entity_ids: List[str] = [
        entity_id
        for (entity_id,) in session.query(distinct(States.entity_id)).all()
        if not instance.entity_filter(entity_id)
    ]

    if len(excluded_entity_ids) != 0:
        batch_purge_before_states = _purge_filtered_states(
            session,
            excluded_entity_ids,
            batch_purge_before_states,
            batch_size_hours,
            subset_size,
        )

    # Check if excluded event_types are in database
    excluded_event_types: List[str] = [
        event_type
        for (event_type,) in session.query(distinct(Events.event_type)).all()
        if event_type in instance.exclude_t
    ]

    if len(excluded_event_types) != 0:
        batch_purge_before_events = _purge_filtered_events(
            session,
            excluded_event_types,
            batch_purge_before_events,
            batch_size_hours,
            subset_size,
        )

    if batch_purge_before_states < utc_now or batch_purge_before_events < utc_now:
        _LOGGER.debug("Purging filter hasn't fully completed yet")
        return False

    return True


def _purge_filtered_states(
    session: Session,
    excluded_entity_ids: List[str],
    batch_purge_before: datetime,
    batch_size_hours: int,
    subset_size: int,
) -> datetime:
    """Handle purging filtered states."""

    query = (
        session.query(States)
        .filter(States.entity_id.in_(excluded_entity_ids))
        .order_by(States.last_updated.asc())
        .limit(1)
    )
    states = execute(query, to_native=True, validate_entity_ids=False)
    if states:
        batch_purge_before = states[0].last_updated + timedelta(hours=batch_size_hours)

    _LOGGER.debug(
        "Purging states before %s that should be filtered",
        batch_purge_before.strftime(DEBUG_DATETIME_FMT),
    )

    event_ids: List[int] = [
        event_id
        for (event_id,) in session.query(States.event_id)
        .filter(States.last_updated < batch_purge_before)
        .filter(States.entity_id.in_(excluded_entity_ids))
        .all()
    ]

    if event_ids:
        deleted_rows_states = (
            session.query(States)
            .filter(States.last_updated < batch_purge_before)
            .filter(States.entity_id.in_(excluded_entity_ids))
            .delete(synchronize_session=False)
        )
        _LOGGER.debug(
            "Deleted %s states because entity_id is excluded", deleted_rows_states
        )

        deleted_rows_events: int = 0
        for i in range(0, len(event_ids), subset_size):
            event_ids_subset = event_ids[i : i + subset_size]
            deleted_rows_events += (
                session.query(Events)
                .filter(Events.event_type == EVENT_STATE_CHANGED)
                .filter(Events.time_fired < batch_purge_before)
                .filter(Events.event_id.in_(event_ids_subset))
                .delete(synchronize_session=False)
            )
        _LOGGER.debug(
            "Deleted %s events because entity_id is excluded", deleted_rows_events
        )

    return batch_purge_before


def _purge_filtered_events(
    session: Session,
    excluded_event_types: List[str],
    batch_purge_before: datetime,
    batch_size_hours: int,
    subset_size: int,
) -> datetime:
    """Handle purging filtered events."""

    query = (
        session.query(Events)
        .filter(Events.event_type.in_(excluded_event_types))
        .order_by(Events.time_fired.asc())
        .limit(1)
    )
    events = execute(query, to_native=True, validate_entity_ids=False)
    if events:
        batch_purge_before = events[0].time_fired + timedelta(hours=batch_size_hours)

    _LOGGER.debug(
        "Purging events before %s the should be filtered",
        batch_purge_before.strftime(DEBUG_DATETIME_FMT),
    )

    event_ids: List[int] = [
        event_id
        for (event_id,) in session.query(Events.event_id)
        .filter(Events.time_fired < batch_purge_before)
        .join(States)
        .filter(Events.event_type.in_(excluded_event_types))
        .all()
    ]

    if event_ids:
        deleted_rows_stats: int = 0
        for i in range(0, len(event_ids), subset_size):
            event_ids_subset = event_ids[i : i + subset_size]
            deleted_rows_stats += (
                session.query(States)
                .filter(States.last_updated < batch_purge_before)
                .filter(States.event_id.in_(event_ids_subset))
                .delete(synchronize_session=False)
            )
        _LOGGER.debug(
            "Deleted %s states because event_type is excluded", deleted_rows_stats
        )

    deleted_rows = (
        session.query(Events)
        .filter(Events.time_fired < batch_purge_before)
        .filter(Events.event_type.in_(excluded_event_types))
        .delete(synchronize_session=False)
    )
    _LOGGER.debug("Deleted %s events because event_type is excluded", deleted_rows)

    return batch_purge_before
