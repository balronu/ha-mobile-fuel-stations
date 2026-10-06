import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiohttp
import pytest

import mobile_fuel_stations.config_flow as config_flow_module
from mobile_fuel_stations.config_flow import MobileFuelStationsConfigFlow, _schema
from mobile_fuel_stations.const import (
    CONF_API_KEY,
    CONF_PETROMAP_API_KEY,
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_PROVIDER_MODE,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_TANKERKOENIG_API_KEY,
    CONF_UPDATE_INTERVAL,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
)
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderDailyBudgetError,
    ProviderInsufficientCreditsError,
    ProviderNetworkError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderCapabilities,
)
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, ProviderRegistration
from mobile_fuel_stations.providers.petromap import (
    async_validate_petromap_credentials,
)


class _FakeResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self.payload = payload

    async def json(self, *, content_type=None):
        del content_type
        return self.payload


class _FakeRequest:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        if self.error:
            raise self.error
        return self.response

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeRequest(self.response, self.error)


def test_usage_validator_is_one_request_and_has_no_places_data():
    session = _FakeSession(_FakeResponse(200))

    asyncio.run(async_validate_petromap_credentials(session, "TEST_SECRET_DO_NOT_LEAK"))

    assert len(session.calls) == 1
    url, kwargs = session.calls[0]
    assert url == "https://api.petromap.eu/v2/usage"
    assert kwargs["headers"] == {"x-api-key": "TEST_SECRET_DO_NOT_LEAK"}
    assert "params" not in kwargs
    assert "places" not in url


@pytest.mark.parametrize(
    ("status", "code", "exception"),
    [
        (401, "INVALID_CREDENTIAL", ProviderAuthError),
        (403, "SCOPE_NOT_PERMITTED", ProviderPermissionError),
        (429, "RATE_LIMITED", ProviderRateLimitError),
        (429, "DAILY_BUDGET_EXHAUSTED", ProviderDailyBudgetError),
        (429, "INSUFFICIENT_CREDITS", ProviderInsufficientCreditsError),
        (503, "ROUTING_UNAVAILABLE", ProviderUnavailableError),
    ],
)
def test_usage_validator_maps_documented_errors_without_retry(status, code, exception):
    session = _FakeSession(_FakeResponse(status, {"error": code}))

    with pytest.raises(exception):
        asyncio.run(async_validate_petromap_credentials(session, "dummy"))
    assert len(session.calls) == 1


def test_usage_validator_maps_timeout_and_connection_errors_without_retry():
    timeout_session = _FakeSession(error=asyncio.TimeoutError())
    with pytest.raises(ProviderTimeoutError):
        asyncio.run(async_validate_petromap_credentials(timeout_session, "dummy"))
    assert len(timeout_session.calls) == 1

    connection_session = _FakeSession(error=aiohttp.ClientConnectionError())
    with pytest.raises(ProviderNetworkError):
        asyncio.run(async_validate_petromap_credentials(connection_session, "dummy"))
    assert len(connection_session.calls) == 1


def test_config_schema_exposes_provider_mode_but_options_do_not():
    user_schema = _schema({}, False, True)
    options_schema = _schema({}, False)
    user_keys = {getattr(key, "schema", key) for key in user_schema.schema}
    option_keys = {getattr(key, "schema", key) for key in options_schema.schema}
    assert CONF_PROVIDER_MODE in user_keys
    assert CONF_API_KEY not in user_keys
    assert CONF_PROVIDER_MODE not in option_keys


def _flow_with_location():
    flow = MobileFuelStationsConfigFlow()
    flow.hass = SimpleNamespace(
        states=SimpleNamespace(
            get=lambda entity_id: SimpleNamespace(
                attributes={"latitude": 49.24, "longitude": 6.99}
            )
            if entity_id == "device_tracker.vehicle"
            else None
        )
    )
    flow.async_show_form = lambda **kwargs: {"type": "form", **kwargs}
    flow.async_create_entry = lambda **kwargs: {"type": "create_entry", **kwargs}
    flow._abort_if_unique_id_configured = lambda: None
    flow.async_set_unique_id = AsyncMock()
    return flow


def _user_input(provider_mode):
    return {
        CONF_PROVIDER_MODE: provider_mode,
        CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        CONF_RADIUS: 20.0,
        CONF_FUEL_TYPE: "diesel",
        CONF_STATION_COUNT: 5,
        CONF_UPDATE_INTERVAL: 15,
        CONF_MOVEMENT_UPDATES: True,
        CONF_MOVEMENT_THRESHOLD: 2.0,
        CONF_COOLDOWN: 5,
    }


def _credential_input(provider_mode):
    if provider_mode == PROVIDER_AUTO:
        return {
            CONF_TANKERKOENIG_API_KEY: "tankerkoenig-secret",
            CONF_PETROMAP_API_KEY: "petromap-secret",
        }
    return {CONF_API_KEY: "provider-secret"}


def test_tankerkoenig_flow_does_not_validate_petromap(monkeypatch):
    flow = _flow_with_location()
    validator = AsyncMock(side_effect=AssertionError("must not be called"))
    monkeypatch.setattr(
        config_flow_module, "async_validate_petromap_credentials", validator
    )

    credentials = asyncio.run(flow.async_step_user(_user_input(PROVIDER_TANKERKOENIG)))
    assert credentials["step_id"] == "tankerkoenig_credentials"
    result = asyncio.run(flow.async_step_tankerkoenig_credentials(_credential_input(PROVIDER_TANKERKOENIG)))

    assert result["type"] == "create_entry"
    assert result["data"][CONF_PROVIDER_MODE] == PROVIDER_TANKERKOENIG
    assert result["data"][CONF_API_KEY] == "provider-secret"
    validator.assert_not_awaited()


def test_enabled_petromap_flow_creates_entry_without_network_request(monkeypatch):
    flow = _flow_with_location()
    validator = AsyncMock(side_effect=AssertionError("setup must not call /usage"))
    monkeypatch.setattr(
        config_flow_module, "async_validate_petromap_credentials", validator
    )

    privacy = asyncio.run(flow.async_step_user(_user_input(PROVIDER_PETROMAP)))
    assert privacy["step_id"] == "petromap_privacy"
    credentials = asyncio.run(flow.async_step_petromap_privacy({}))
    assert credentials["step_id"] == "petromap_credentials"
    result = asyncio.run(flow.async_step_petromap_credentials(_credential_input(PROVIDER_PETROMAP)))

    assert result["type"] == "create_entry"
    assert result["data"][CONF_PROVIDER_MODE] == PROVIDER_PETROMAP
    assert result["data"][CONF_API_KEY] == "provider-secret"
    validator.assert_not_awaited()


def test_auto_flow_creates_entry_with_dual_credentials_without_network_request(monkeypatch):
    flow = _flow_with_location()
    validator = AsyncMock(side_effect=AssertionError("setup must not call /usage"))
    monkeypatch.setattr(config_flow_module, "async_validate_petromap_credentials", validator)

    privacy = asyncio.run(flow.async_step_user(_user_input(PROVIDER_AUTO)))
    assert privacy["step_id"] == "auto_privacy"
    credentials = asyncio.run(flow.async_step_auto_privacy({}))
    assert credentials["step_id"] == "auto_credentials"
    result = asyncio.run(flow.async_step_auto_credentials(_credential_input(PROVIDER_AUTO)))

    assert result["type"] == "create_entry"
    assert result["data"][CONF_PROVIDER_MODE] == PROVIDER_AUTO
    assert result["data"][CONF_TANKERKOENIG_API_KEY] == "tankerkoenig-secret"
    assert result["data"][CONF_PETROMAP_API_KEY] == "petromap-secret"
    assert CONF_API_KEY not in result["data"]
    validator.assert_not_awaited()


def test_auto_credential_model_requires_both_keys_before_validation():
    flow = _flow_with_location()
    flow._validate_petromap_key = AsyncMock(return_value=None)

    asyncio.run(flow.async_step_user(_user_input(PROVIDER_AUTO)))
    asyncio.run(flow.async_step_auto_privacy({}))
    result = asyncio.run(
        flow.async_step_auto_credentials(
            {CONF_TANKERKOENIG_API_KEY: "tankerkoenig-secret"}
        )
    )

    assert result["type"] == "form"
    assert result["errors"][CONF_PETROMAP_API_KEY] == "api_key_required"
    flow._validate_petromap_key.assert_not_awaited()


@pytest.mark.parametrize("provider_mode", [PROVIDER_PETROMAP, PROVIDER_AUTO])
def test_enabled_external_provider_flow_creates_entry_without_network_request(monkeypatch, provider_mode):
    flow = _flow_with_location()
    validator = AsyncMock(return_value=None)
    monkeypatch.setattr(config_flow_module, "async_validate_petromap_credentials", validator)
    monkeypatch.setitem(
        PROVIDER_REGISTRY,
        provider_mode,
        ProviderRegistration(
            provider_id=provider_mode,
            factory=lambda session, key: None,
            enabled=True,
            capabilities=ProviderCapabilities(),
        ),
    )
    monkeypatch.setattr(config_flow_module, "async_get_clientsession", lambda hass: object())

    privacy = asyncio.run(flow.async_step_user(_user_input(provider_mode)))
    assert privacy["step_id"] in {"petromap_privacy", "auto_privacy"}
    credentials = asyncio.run(getattr(flow, f"async_step_{privacy['step_id']}")({}))
    result = asyncio.run(
        getattr(flow, f"async_step_{credentials['step_id']}")(
            _credential_input(provider_mode)
        )
    )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_PROVIDER_MODE] == provider_mode
    if provider_mode == PROVIDER_AUTO:
        assert result["data"][CONF_TANKERKOENIG_API_KEY] == "tankerkoenig-secret"
        assert result["data"][CONF_PETROMAP_API_KEY] == "petromap-secret"
        assert CONF_API_KEY not in result["data"]
    validator.assert_not_awaited()


def test_external_privacy_step_does_not_validate_or_request():
    flow = _flow_with_location()
    validator = AsyncMock(side_effect=AssertionError("validation is deferred"))
    flow._validate_petromap_key = validator

    result = asyncio.run(flow.async_step_user(_user_input(PROVIDER_PETROMAP)))

    assert result["step_id"] == "petromap_privacy"
    validator.assert_not_awaited()


def test_config_flow_maps_validator_errors_without_leaking_key():
    flow = _flow_with_location()
    flow.hass.config_entries = SimpleNamespace()
    flow._validate_petromap_key = AsyncMock(return_value="permission_error")

    # The registry is disabled in production; this tests the pure mapping helper.
    assert flow._validation_error(ProviderAuthError("INVALID_CREDENTIAL")) == "invalid_auth"
    assert flow._validation_error(ProviderPermissionError("SCOPE_NOT_PERMITTED")) == "permission_error"
    assert flow._validation_error(ProviderRateLimitError("RATE_LIMITED")) == "rate_limited"
    assert flow._validation_error(ProviderDailyBudgetError("DAILY_BUDGET_EXHAUSTED")) == "budget_exhausted"
    assert flow._validation_error(ProviderInsufficientCreditsError("INSUFFICIENT_CREDITS")) == "budget_exhausted"
    assert flow._validation_error(ProviderTimeoutError("timeout")) == "cannot_connect"
    assert flow._validation_error(ProviderNetworkError("network")) == "cannot_connect"
    assert flow._validation_error(ProviderResponseError("response")) == "unknown"


def test_reauth_updates_only_explicit_key_without_usage_validation():
    flow = MobileFuelStationsConfigFlow()
    entry = SimpleNamespace(
        data={
            CONF_API_KEY: "OLD_SECRET",
            CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
            CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        }
    )
    flow._get_reauth_entry = lambda: entry
    flow._validate_petromap_key = AsyncMock(
        side_effect=AssertionError("reauth must not call /usage")
    )
    flow.async_update_reload_and_abort = lambda current, **kwargs: {
        "type": "abort",
        "entry": current,
        **kwargs,
    }

    result = asyncio.run(
        flow.async_step_reauth_confirm({CONF_API_KEY: "NEW_SECRET"})
    )

    assert result["type"] == "abort"
    assert result["data_updates"] == {CONF_API_KEY: "NEW_SECRET"}
    assert entry.data[CONF_API_KEY] == "OLD_SECRET"
    flow._validate_petromap_key.assert_not_awaited()


def test_reauth_missing_key_keeps_old_key_and_does_not_reload():
    flow = MobileFuelStationsConfigFlow()
    entry = SimpleNamespace(data={CONF_API_KEY: "OLD_SECRET"})
    flow._get_reauth_entry = lambda: entry
    flow._validate_petromap_key = AsyncMock(
        side_effect=AssertionError("reauth must not call /usage")
    )
    reload_helper = AsyncMock()
    flow.async_update_reload_and_abort = reload_helper

    result = asyncio.run(
        flow.async_step_reauth_confirm({CONF_API_KEY: ""})
    )

    assert result["type"] == "form"
    assert result["errors"][CONF_API_KEY] == "api_key_required"
    assert entry.data[CONF_API_KEY] == "OLD_SECRET"
    reload_helper.assert_not_awaited()


def test_auto_reauth_updates_only_petromap_key_without_usage_validation():
    flow = MobileFuelStationsConfigFlow()
    entry = SimpleNamespace(
        data={
            CONF_TANKERKOENIG_API_KEY: "TK_OLD",
            CONF_PETROMAP_API_KEY: "PM_OLD",
            CONF_PROVIDER_MODE: PROVIDER_AUTO,
        }
    )
    flow._get_reauth_entry = lambda: entry
    flow._validate_petromap_key = AsyncMock(side_effect=AssertionError("reauth must not call /usage"))
    flow.async_update_reload_and_abort = lambda current, **kwargs: {
        "type": "abort",
        "entry": current,
        **kwargs,
    }

    result = asyncio.run(
        flow.async_step_reauth_auto_confirm({CONF_PETROMAP_API_KEY: "PM_NEW"})
    )

    assert result["type"] == "abort"
    assert result["data_updates"] == {CONF_PETROMAP_API_KEY: "PM_NEW"}
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "TK_OLD"
    assert entry.data[CONF_PETROMAP_API_KEY] == "PM_OLD"
    flow._validate_petromap_key.assert_not_awaited()
