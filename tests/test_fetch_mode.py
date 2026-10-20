"""Regression tests for automatic and administrator-controlled fetch modes."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.config_entries import ConfigEntryState

from mobile_fuel_stations import _async_manual_refresh_service, _require_admin
from mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator
from mobile_fuel_stations.const import (
    CONF_FETCH_MODE,
    DEFAULT_FETCH_MODE,
    FETCH_MODE_AUTOMATIC,
    FETCH_MODE_MANUAL,
)


def _manual_coordinator() -> MobileFuelStationsCoordinator:
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.fetch_mode = FETCH_MODE_MANUAL
    coordinator._manual_refresh_in_progress = False
    coordinator._manual_refresh_lock = asyncio.Lock()
    coordinator._has_valid_provider_result = False
    coordinator.stations = []
    coordinator.last_update_result = None
    coordinator.last_update_error_class = None
    return coordinator


def test_default_fetch_mode_is_automatic():
    assert DEFAULT_FETCH_MODE == FETCH_MODE_AUTOMATIC


def test_manual_update_path_does_not_call_provider(monkeypatch):
    coordinator = _manual_coordinator()
    provider = AsyncMock()
    coordinator._manual_refresh_in_progress = False
    monkeypatch.setattr(coordinator, "async_update_nakordoni_usage", AsyncMock())

    result = asyncio.run(coordinator._async_update_data())

    assert result is None
    assert coordinator.last_update_result == "manual_mode"
    provider.assert_not_awaited()


def test_manual_mode_ignores_gps_and_startup_recovery_triggers(monkeypatch):
    coordinator = _manual_coordinator()
    movement = Mock()
    recovery = Mock()
    monkeypatch.setattr(coordinator, "_schedule_movement_refresh", movement)
    monkeypatch.setattr(coordinator, "_request_recovery_refresh", recovery)

    coordinator._process_gps_event(SimpleNamespace(), "state_changed")
    coordinator.async_schedule_startup_recovery()

    movement.assert_not_called()
    recovery.assert_not_called()


def test_manual_refresh_performs_exactly_one_coordinator_request():
    coordinator = _manual_coordinator()

    async def request_once():
        coordinator.last_update_result = "provider_success"

    coordinator.async_request_refresh = request_once
    asyncio.run(coordinator.async_manual_refresh())

    assert coordinator.last_update_result == "provider_success"
    assert coordinator._manual_refresh_in_progress is False


def test_parallel_manual_refresh_is_rejected():
    coordinator = _manual_coordinator()
    asyncio.run(coordinator._manual_refresh_lock.acquire())
    try:
        with pytest.raises(UpdateFailed, match="already in progress"):
            asyncio.run(coordinator.async_manual_refresh())
    finally:
        coordinator._manual_refresh_lock.release()


def test_admin_check_rejects_dashboard_without_admin_user():
    user = SimpleNamespace(is_admin=False)
    hass = SimpleNamespace(auth=SimpleNamespace(async_get_user=AsyncMock(return_value=user)))
    call = SimpleNamespace(hass=hass, context=SimpleNamespace(user_id="viewer"))

    with pytest.raises(Exception, match="Administrator permission required"):
        asyncio.run(_require_admin(hass, call))


def test_manual_refresh_service_targets_one_entry():
    coordinator = _manual_coordinator()
    coordinator.async_manual_refresh = AsyncMock()
    entry = SimpleNamespace(
        domain="mobile_fuel_stations",
        state=ConfigEntryState.LOADED,
        runtime_data=coordinator,
    )
    user = SimpleNamespace(is_admin=True)
    hass = SimpleNamespace(
        auth=SimpleNamespace(async_get_user=AsyncMock(return_value=user)),
        config_entries=SimpleNamespace(async_get_entry=Mock(return_value=entry)),
    )
    call = SimpleNamespace(
        hass=hass,
        context=SimpleNamespace(user_id="admin"),
        data={"entry_id": "entry-opel"},
    )

    asyncio.run(_async_manual_refresh_service(call))

    coordinator.async_manual_refresh.assert_awaited_once_with()
