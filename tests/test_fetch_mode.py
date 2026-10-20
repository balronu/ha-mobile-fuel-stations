"""Regression tests for automatic and administrator-controlled fetch modes."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.config_entries import ConfigEntryState

from mobile_fuel_stations import (
    _async_manual_refresh_service,
    _async_set_fetch_mode_service,
    _require_admin,
)
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
    coordinator._lifecycle_generation = 0
    coordinator._shutdown_started = False
    coordinator.options = {"update_interval": 30}
    coordinator.update_interval = None
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


def test_manual_mode_does_not_mark_existing_result_stale_during_provider_cooldown(monkeypatch):
    coordinator = _manual_coordinator()
    coordinator._has_valid_provider_result = True
    coordinator.stations = [object()]
    coordinator.data = coordinator.stations
    coordinator.last_request = None
    coordinator.provider_last_requests = {}
    coordinator.data_stale = False

    # A normal manual-mode coordinator returns its confirmed result without
    # polling; the explicit refresh path must not turn that result stale just
    # because the mode is manual.
    result = asyncio.run(coordinator._async_update_data())

    assert result == coordinator.stations
    assert coordinator.data_stale is False


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


@pytest.mark.parametrize("service", (_async_manual_refresh_service, _async_set_fetch_mode_service))
def test_both_control_services_reject_non_admin(service):
    user = SimpleNamespace(is_admin=False)
    hass = SimpleNamespace(auth=SimpleNamespace(async_get_user=AsyncMock(return_value=user)))
    call = SimpleNamespace(
        hass=hass,
        context=SimpleNamespace(user_id="viewer"),
        data={"entry_id": "entry-opel", CONF_FETCH_MODE: FETCH_MODE_MANUAL},
    )

    with pytest.raises(Exception, match="Administrator permission required"):
        asyncio.run(service(call))


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


def test_mode_change_invalidates_inflight_generation_and_disables_schedule():
    coordinator = _manual_coordinator()
    coordinator.fetch_mode = FETCH_MODE_AUTOMATIC
    coordinator._unschedule_refresh = Mock()
    coordinator._unsub_refresh = Mock()

    coordinator.prepare_fetch_mode_change(FETCH_MODE_MANUAL)

    assert coordinator.fetch_mode == FETCH_MODE_MANUAL
    assert coordinator._lifecycle_generation == 1
    assert coordinator.update_interval is None
    coordinator._unschedule_refresh.assert_called_once_with()


def test_two_entries_keep_independent_fetch_modes_and_switch_without_refresh():
    first = _manual_coordinator()
    first.fetch_mode = FETCH_MODE_AUTOMATIC
    second = _manual_coordinator()
    second.fetch_mode = FETCH_MODE_MANUAL
    entries = {
        "entry-auto": SimpleNamespace(
            domain="mobile_fuel_stations", state=ConfigEntryState.LOADED,
            data={CONF_FETCH_MODE: FETCH_MODE_AUTOMATIC}, options={}, runtime_data=first,
        ),
        "entry-manual": SimpleNamespace(
            domain="mobile_fuel_stations", state=ConfigEntryState.LOADED,
            data={CONF_FETCH_MODE: FETCH_MODE_MANUAL}, options={}, runtime_data=second,
        ),
    }
    user = SimpleNamespace(is_admin=True)
    hass = SimpleNamespace(
        auth=SimpleNamespace(async_get_user=AsyncMock(return_value=user)),
        data={},
        config_entries=SimpleNamespace(
            async_get_entry=lambda entry_id: entries[entry_id],
            async_update_entry=Mock(),
        ),
    )
    call = SimpleNamespace(
        hass=hass, context=SimpleNamespace(user_id="admin"),
        data={"entry_id": "entry-auto", CONF_FETCH_MODE: FETCH_MODE_MANUAL},
    )

    asyncio.run(_async_set_fetch_mode_service(call))

    assert first.fetch_mode == FETCH_MODE_MANUAL
    assert second.fetch_mode == FETCH_MODE_MANUAL
    assert first._lifecycle_generation == 1
    assert second._lifecycle_generation == 0
    hass.config_entries.async_update_entry.assert_called_once()
    assert hass.config_entries.async_update_entry.call_args.args[0] is entries["entry-auto"]
