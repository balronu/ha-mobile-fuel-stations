"""Regression tests for the stationary Nakordoni credit guard."""

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mobile_fuel_stations.const import (
    CONF_LOCATION_ENTITY,
    CONF_PROVIDER_MODE,
    FETCH_MODE_AUTOMATIC,
    PROVIDER_AUTO,
    PROVIDER_NAKORDONI,
)
from mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator


class _StopAfterGuard(Exception):
    """Sentinel proving that the stationary guard did not return."""


def _coordinator(*, position=(49.2, 7.0), age=timedelta(hours=1)):
    now = datetime.now(timezone.utc)
    state = SimpleNamespace(
        state="home",
        attributes={"latitude": position[0], "longitude": position[1]},
        last_reported=now,
        last_updated=now,
        last_changed=now,
    )
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.fetch_mode = FETCH_MODE_AUTOMATIC
    coordinator.options = {
        CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        CONF_PROVIDER_MODE: PROVIDER_AUTO,
    }
    coordinator.hass = SimpleNamespace(
        states=SimpleNamespace(get=lambda _entity: state),
    )
    coordinator._cache_provider = PROVIDER_NAKORDONI
    coordinator._has_valid_provider_result = True
    coordinator.reference_position = (49.2, 7.0)
    coordinator.last_successful_update = now - age
    coordinator.stations = [object()]
    coordinator.data = coordinator.stations
    coordinator.last_update_result = None
    coordinator.last_update_attempt = None
    coordinator.fallback_attempted = False
    coordinator.fallback_provider = None
    coordinator.fallback_result = None
    coordinator.fallback_skip_reason = None
    coordinator._previous_result = lambda: coordinator.stations
    coordinator.async_update_nakordoni_usage = AsyncMock(
        side_effect=_StopAfterGuard
    )
    return coordinator


def test_stationary_nakordoni_poll_reuses_cache_without_usage_or_search():
    coordinator = _coordinator()

    result = asyncio.run(coordinator._async_update_data())

    assert result == coordinator.stations
    assert coordinator.last_update_result == "stationary_cache"
    coordinator.async_update_nakordoni_usage.assert_not_awaited()


@pytest.mark.parametrize(
    "position, age",
    [((49.2 + 0.027, 7.0), timedelta(hours=1)), ((49.2, 7.0), timedelta(hours=25))],
)
def test_movement_or_expired_cache_reaches_refresh_path(position, age):
    coordinator = _coordinator(position=position, age=age)

    with pytest.raises(_StopAfterGuard):
        asyncio.run(coordinator._async_update_data())

    coordinator.async_update_nakordoni_usage.assert_awaited_once()

