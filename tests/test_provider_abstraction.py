import asyncio

import pytest

from mobile_fuel_stations.const import (
    CONF_PETROMAP_API_KEY,
    CONF_PROVIDER_MODE,
    CONF_TANKERKOENIG_API_KEY,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
)
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, create_provider
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
    ProviderDisabledError,
    StationSearchQuery,
    UnknownProviderError,
)
from mobile_fuel_stations.providers.petromap import PetromapProvider
from mobile_fuel_stations.providers.tankerkoenig import TankerkoenigProvider


class FakeResponse:
    def __init__(self, payload=None, status=200, headers=None):
        self.status = status
        self.payload = payload if payload is not None else {"ok": True, "status": "ok", "stations": []}
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def raise_for_status(self):
        return None

    async def json(self, content_type=None):
        return self.payload


class FakeSession:
    def __init__(self, response=None):
        self.calls = []
        self.response = response or FakeResponse()

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        return self.response


class SessionWithCloseGuard(FakeSession):
    def __init__(self):
        super().__init__()
        self.close_calls = 0

    async def close(self):
        self.close_calls += 1


def test_legacy_config_defaults_to_tankerkoenig_provider():
    provider = create_provider(object(), {"api_key": "legacy-secret"})

    assert isinstance(provider, TankerkoenigProvider)


def test_explicit_tankerkoenig_mode_uses_same_provider():
    provider = create_provider(
        object(), {"api_key": "secret", CONF_PROVIDER_MODE: PROVIDER_TANKERKOENIG}
    )

    assert isinstance(provider, TankerkoenigProvider)


def test_explicit_provider_modes_use_only_their_provider_key():
    tk_provider = create_provider(
        object(),
        {
            CONF_PROVIDER_MODE: PROVIDER_TANKERKOENIG,
            CONF_TANKERKOENIG_API_KEY: "tk-secret-dummy",
            CONF_PETROMAP_API_KEY: "pm-secret-dummy",
        },
    )
    pm_provider = create_provider(
        object(),
        {
            CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
            CONF_TANKERKOENIG_API_KEY: "tk-secret-dummy",
            CONF_PETROMAP_API_KEY: "pm-secret-dummy",
        },
    )

    assert isinstance(tk_provider, TankerkoenigProvider)
    assert tk_provider._api_key == "tk-secret-dummy"
    assert isinstance(pm_provider, PetromapProvider)
    assert pm_provider._api_key == "pm-secret-dummy"


def test_petromap_construction_injects_shared_session_without_io_or_close():
    session = SessionWithCloseGuard()
    secret = "TEST_SECRET_DO_NOT_LEAK"

    provider = PetromapProvider(session, secret)

    assert provider._session is session
    assert session.calls == []
    assert session.close_calls == 0
    assert secret not in repr(provider)
    assert secret not in repr(provider.last_response_metadata)


def test_petromap_mode_uses_enabled_provider_without_network_at_construction():
    session = FakeSession()
    provider = create_provider(session, {"api_key": "secret", CONF_PROVIDER_MODE: "petromap"})
    assert isinstance(provider, PetromapProvider)
    assert provider._session is session
    assert provider._api_key == "secret"
    assert session.calls == []


def test_unknown_provider_mode_fails_before_network_access():
    session = FakeSession()
    with pytest.raises(UnknownProviderError):
        create_provider(session, {"api_key": "secret", CONF_PROVIDER_MODE: "unknown"})
    assert session.calls == []


def test_disabled_registry_entries_have_no_factory():
    assert PROVIDER_REGISTRY["petromap"].enabled is True
    assert PROVIDER_REGISTRY["petromap"].factory is PetromapProvider
    assert PROVIDER_REGISTRY["auto"].enabled is False
    assert PROVIDER_REGISTRY["auto"].factory is None


def test_auto_mode_remains_disabled_before_network_access():
    session = FakeSession()
    with pytest.raises(ProviderDisabledError):
        create_provider(session, {"api_key": "secret", CONF_PROVIDER_MODE: "auto"})
    assert session.calls == []


def test_tankerkoenig_request_parameters_remain_unchanged():
    session = FakeSession()
    provider = TankerkoenigProvider(session, "secret")

    asyncio.run(
        provider.async_search(
            StationSearchQuery(
                latitude=50.12345678,
                longitude=8.87654321,
                radius_km=25.0,
                fuel_type="diesel",
            )
        )
    )

    _, params, timeout = session.calls[0]
    assert params == {
        "lat": "50.1234568",
        "lng": "8.8765432",
        "rad": "25",
        "sort": "price",
        "type": "diesel",
        "apikey": "secret",
    }
    assert timeout == 15


@pytest.mark.parametrize(
    ("status", "error_type"),
    [(401, ProviderAuthError), (403, ProviderAuthError), (429, ProviderRateLimitError), (503, ProviderUnavailableError)],
)
def test_tankerkoenig_classifies_http_failures_without_secret_text(status, error_type):
    provider = TankerkoenigProvider(FakeSession(FakeResponse(status=status)), "SECRET_NOT_EXPOSED")

    with pytest.raises(error_type) as caught:
        asyncio.run(provider.async_search(StationSearchQuery(50, 8, 5, "diesel")))

    assert "SECRET_NOT_EXPOSED" not in str(caught.value)
    assert caught.value.diagnostics.http_status == status


def test_tankerkoenig_rejects_malformed_success_payload():
    provider = TankerkoenigProvider(FakeSession(FakeResponse({"ok": True, "status": "ok", "stations": {}})), "secret")

    with pytest.raises(ProviderResponseError) as caught:
        asyncio.run(provider.async_search(StationSearchQuery(50, 8, 5, "diesel")))

    assert caught.value.diagnostics.error_code == "invalid_stations_payload"


def test_tankerkoenig_rejects_non_object_json_payload():
    provider = TankerkoenigProvider(FakeSession(FakeResponse([])), "secret")

    with pytest.raises(ProviderResponseError) as caught:
        asyncio.run(provider.async_search(StationSearchQuery(50, 8, 5, "diesel")))

    assert caught.value.diagnostics.error_code == "invalid_json_shape"


def test_tankerkoenig_classifies_key_and_rate_status_without_raw_response():
    for status, error_type in (("ERROR_INVALID_KEY", ProviderAuthError), ("ERROR_RATE_LIMIT", ProviderRateLimitError)):
        provider = TankerkoenigProvider(
            FakeSession(FakeResponse({"ok": False, "status": status, "stations": []})), "secret"
        )
        with pytest.raises(error_type) as caught:
            asyncio.run(provider.async_search(StationSearchQuery(50, 8, 5, "diesel")))
        assert status in caught.value.diagnostics.error_code
