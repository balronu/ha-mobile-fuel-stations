import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.config_entries import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from mobile_fuel_stations import coordinator as coordinator_module
from mobile_fuel_stations.const import (
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_PROVIDER_MODE,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    PROVIDER_PETROMAP,
)
from mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator
from mobile_fuel_stations.diagnostics import async_get_config_entry_diagnostics
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderRequestDiagnostics,
    ProviderTimeoutError,
    ProviderUnavailableError,
    Station,
)
from mobile_fuel_stations.providers.petromap import PetromapProvider


class _Store:
    def __init__(self):
        self.saved = None

    async def async_load(self):
        return self.saved

    async def async_save(self, data):
        self.saved = data


class _Provider:
    def __init__(self, result=None, error=None):
        self.result = result if result is not None else []
        self.error = error
        self.calls = []

    async def async_search(self, query):
        self.calls.append(query)
        if self.error:
            raise self.error
        return self.result


def _coordinator(provider, fuel="diesel"):
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.hass = SimpleNamespace(data={})
    coordinator.entry = SimpleNamespace(
        entry_id="test-entry",
        async_start_reauth=lambda *args, **kwargs: None,
    )
    coordinator.options = {
        CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        CONF_RADIUS: 25.0,
        CONF_FUEL_TYPE: fuel,
        CONF_STATION_COUNT: 3,
        CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
    }
    coordinator.client = provider
    coordinator.stations = []
    coordinator.nearest_station = None
    coordinator.cheapest_station = None
    coordinator.last_successful_update = None
    coordinator.reference_position = None
    coordinator.last_request = None
    coordinator.last_update_attempt = None
    coordinator.last_update_error_at = None
    coordinator.last_update_error_class = None
    coordinator.last_update_error_provider = None
    coordinator.last_retry_after = None
    coordinator.data_stale = False
    coordinator.recovery_status = "never"
    coordinator.consecutive_failures = 0
    coordinator._retry_not_before = None
    coordinator._movement_refresh_scheduled = False
    coordinator._movement_refresh_task = None
    coordinator._store = _Store()
    coordinator._provider_status_store = _Store()
    coordinator.provider_status = {}
    coordinator.country_auto_context = SimpleNamespace(
        observe_position=lambda position: None
    )
    return coordinator


def _station():
    return Station(
        "petro-1", "Demo", "Petromap", 1.8, 1.0, True,
        "Street", "1", "12345", "Town", 49.2, 7.0,
    )


def test_petromap_diesel_refresh_uses_one_search_query(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    result = asyncio.run(coordinator._async_update_data())

    assert result == [_station()]
    assert len(provider.calls) == 1
    assert provider.calls[0].fuel_type == "diesel"
    assert provider.calls[0].latitude == 49.2
    assert provider.calls[0].longitude == 7.0
    assert coordinator.hass.data["mobile_fuel_stations"]["provider_status"]["test-entry"][PROVIDER_PETROMAP]["status"] == "success"
    assert coordinator._provider_status_store.saved[PROVIDER_PETROMAP]["status"] == "success"


def test_startup_without_gps_keeps_coordinator_setup_recoverable(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: None)

    assert asyncio.run(coordinator._async_update_data()) is None
    assert coordinator.recovery_status == "awaiting_location"
    assert provider.calls == []


def test_successful_empty_provider_response_is_real_zero(monkeypatch):
    provider = _Provider([])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    assert asyncio.run(coordinator._async_update_data()) == []
    assert coordinator.recovery_status == "success"


def test_first_valid_gps_after_startup_schedules_one_refresh(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    coordinator._movement_refresh_scheduled = False
    create_task = Mock(side_effect=lambda coroutine: coroutine.close())
    coordinator.hass = SimpleNamespace(
        data={},
        async_create_task=create_task,
    )
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    coordinator._async_position_changed(SimpleNamespace())
    coordinator._async_position_changed(SimpleNamespace())

    create_task.assert_called_once()


def test_startup_recovery_rechecks_current_gps_without_event(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    coordinator.recovery_status = "awaiting_location"
    create_task = Mock(side_effect=lambda coroutine: coroutine.close())
    coordinator.hass = SimpleNamespace(
        data={},
        async_create_task=create_task,
    )
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    coordinator.async_schedule_startup_recovery()
    coordinator.async_schedule_startup_recovery()

    create_task.assert_called_once()


def test_shutdown_unsubscribes_and_cancels_pending_recovery_task(monkeypatch):
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    unsubscribe = Mock()
    task = Mock()
    task.done.return_value = False
    coordinator._unsub_position = unsubscribe
    coordinator._movement_refresh_task = task

    core_shutdown = AsyncMock()
    monkeypatch.setattr(DataUpdateCoordinator, "async_shutdown", core_shutdown)
    asyncio.run(coordinator.async_shutdown())

    unsubscribe.assert_called_once_with()
    task.cancel.assert_called_once_with()
    core_shutdown.assert_awaited_once_with()
    assert coordinator._unsub_position is None
    assert coordinator._movement_refresh_task is None


def test_data_update_coordinator_first_listener_registers_periodic_refresh():
    """Exercise HA Core's real listener/periodic-refresh registration path."""

    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator._listeners = {}
    coordinator._last_listener_id = 0
    coordinator._schedule_refresh = Mock()
    coordinator._unschedule_refresh = Mock()
    coordinator._debounced_refresh = SimpleNamespace(async_cancel=Mock())

    remove_first = DataUpdateCoordinator.async_add_listener(coordinator, Mock())
    remove_second = DataUpdateCoordinator.async_add_listener(coordinator, Mock())

    coordinator._schedule_refresh.assert_called_once_with()
    assert len(coordinator._listeners) == 2
    remove_first()
    assert len(coordinator._listeners) == 1
    remove_second()
    assert coordinator._listeners == {}


def test_coordinator_keeps_ha_core_periodic_scheduler():
    """The integration must not override HA Core's timer scheduler."""

    assert (
        MobileFuelStationsCoordinator._schedule_refresh
        is DataUpdateCoordinator._schedule_refresh
    )


def test_diagnostics_report_lifecycle_without_coordinates_or_secrets():
    coordinator = SimpleNamespace(
        _listeners={index: (Mock(), None) for index in range(1, 7)},
        _unsub_refresh=Mock(),
        update_interval=timedelta(minutes=15),
        gps_available=False,
        gps_listener_registered=True,
        last_successful_update=None,
        last_update_attempt=None,
        last_update_result="gps_unavailable",
        last_provider_attempt=None,
        last_provider_success=None,
        recovery_status="awaiting_location",
        recovery_task_status="not_scheduled",
        last_update_success=True,
        data=None,
        last_exception=None,
    )
    entry = SimpleNamespace(
        entry_id="diagnostic-entry",
        data={"api_key": "SECRET", "location_entity": "device_tracker.vehicle"},
        options={},
        runtime_data=coordinator,
    )
    hass = SimpleNamespace(data={})

    result = asyncio.run(async_get_config_entry_diagnostics(hass, entry))

    assert result["runtime"]["coordinator_listener_count"] == 6
    assert result["runtime"]["coordinator_update_interval_minutes"] == 15
    assert result["runtime"]["periodic_refresh_scheduled"] is True
    assert result["runtime"]["periodic_refresh_callback_status"] == "scheduled"
    assert result["runtime"]["next_refresh_deadline"] is None
    assert result["runtime"]["gps_available"] is False
    assert "api_key" not in result["config"]
    assert "SECRET" not in str(result)


def test_diagnostics_report_unknown_during_refresh_without_claiming_missing_timer():
    coordinator = SimpleNamespace(
        _listeners={1: (Mock(), None)},
        _unsub_refresh=None,
        update_interval=timedelta(minutes=15),
        gps_available=True,
        gps_listener_registered=True,
        last_successful_update=None,
        last_update_attempt=None,
        last_update_result="started",
        last_provider_attempt=None,
        last_provider_success=None,
        recovery_status="success",
        recovery_task_status="not_scheduled",
        last_update_success=True,
        data=[],
        last_exception=None,
    )
    entry = SimpleNamespace(
        entry_id="diagnostic-entry", data={}, options={}, runtime_data=coordinator
    )

    result = asyncio.run(async_get_config_entry_diagnostics(SimpleNamespace(data={}), entry))

    assert result["runtime"]["periodic_refresh_scheduled"] is None
    assert result["runtime"]["periodic_refresh_callback_status"] == "unknown"


def test_three_regular_poll_cycles_follow_initial_gps_miss(monkeypatch):
    """A failed initial GPS read must not prevent later regular update calls."""

    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    positions = iter([None, (49.2, 7.0), (49.2, 7.0), (49.2, 7.0)])
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: next(positions))

    assert asyncio.run(coordinator._async_update_data()) is None
    assert asyncio.run(coordinator._async_update_data()) == [_station()]
    assert asyncio.run(coordinator._async_update_data()) == [_station()]
    assert asyncio.run(coordinator._async_update_data()) == [_station()]

    assert len(provider.calls) == 3
    assert coordinator.last_update_result == "provider_success"
    assert coordinator.last_provider_success is not None


def test_petromap_e5_refresh_uses_one_search_query(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider, fuel="e5")
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    asyncio.run(coordinator._async_update_data())

    assert len(provider.calls) == 1
    assert provider.calls[0].fuel_type == "e5"


class _NoRequestSession:
    def __init__(self):
        self.calls = 0

    def get(self, *args, **kwargs):
        del args, kwargs
        self.calls += 1
        raise AssertionError("Petromap e10 must be rejected before HTTP")


def test_petromap_e10_uses_capability_declared_e5_fallback(monkeypatch):
    provider = PetromapProvider(object(), "dummy")
    provider.async_search = AsyncMock(return_value=[])
    coordinator = _coordinator(provider, fuel="e10")
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    asyncio.run(coordinator._async_update_data())
    provider.async_search.assert_awaited_once()
    assert provider.async_search.await_args.args[0].fuel_type == "e5"


def test_petromap_401_requests_reauth(monkeypatch):
    provider = _Provider(error=ProviderAuthError("INVALID_CREDENTIAL"))
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    with pytest.raises(ConfigEntryAuthFailed):
        asyncio.run(coordinator._async_update_data())
    assert len(provider.calls) == 1


def test_petromap_rate_limit_keeps_last_valid_stations(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))
    asyncio.run(coordinator._async_update_data())
    previous = coordinator.stations

    provider.error = ProviderRateLimitError("RATE_LIMITED")
    stale = asyncio.run(coordinator._async_update_data())

    assert stale == previous
    assert coordinator.stations == previous
    assert coordinator.data_stale is True
    assert coordinator.last_update_error_class == "ProviderRateLimitError"
    assert len(provider.calls) == 2

    provider.error = None
    recovered = asyncio.run(coordinator._async_update_data())

    assert recovered == previous
    assert coordinator.data_stale is False
    assert coordinator.recovery_status == "recovered"
    assert coordinator.consecutive_failures == 0
    assert len(provider.calls) == 3


def test_transient_timeout_without_cached_data_keeps_entities_recoverable(monkeypatch):
    provider = _Provider(error=ProviderTimeoutError("timeout"))
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    assert asyncio.run(coordinator._async_update_data()) is None

    assert coordinator.data_stale is False
    assert coordinator.last_update_error_class == "ProviderTimeoutError"


def test_retry_after_prevents_extra_provider_call_until_window_expires(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))
    asyncio.run(coordinator._async_update_data())

    error = ProviderRateLimitError("RATE_LIMITED")
    error.retry_after = 60
    provider.error = error
    asyncio.run(coordinator._async_update_data())
    assert coordinator.last_retry_after == 60
    assert len(provider.calls) == 2

    asyncio.run(coordinator._async_update_data())
    assert len(provider.calls) == 2


def test_nakordoni_failure_metadata_is_published_before_recovery_retry(monkeypatch):
    provider = _Provider(error=ProviderRateLimitError("qps_exceeded"))
    provider.error.diagnostics = ProviderRequestDiagnostics(
        "nakordoni", 429, "qps_exceeded", 60, 1000, 999, False, False
    )
    coordinator = _coordinator(provider)
    coordinator.options[CONF_PROVIDER_MODE] = "nakordoni"
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    assert asyncio.run(coordinator._async_update_data()) is None

    assert coordinator.hass.data["mobile_fuel_stations"]["last_request_diagnostics"]["test-entry"] == {
        "provider": "nakordoni",
        "http_status": 429,
        "error_code": "qps_exceeded",
        "retry_after": 60,
        "quota_limit": 1000,
        "quota_remaining": 999,
        "request_success": False,
        "response_ok": False,
    }


@pytest.mark.parametrize(
    "error",
    [
        ProviderRateLimitError("RATE_LIMITED"),
        ProviderUnavailableError("ROUTING_UNAVAILABLE"),
        ProviderTimeoutError("timeout"),
        ProviderResponseError("malformed"),
    ],
)
def test_petromap_non_auth_failures_leave_startup_recovery_available(
    monkeypatch, error
):
    provider = _Provider(error=error)
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    assert asyncio.run(coordinator._async_update_data()) is None
    assert len(provider.calls) == 1
