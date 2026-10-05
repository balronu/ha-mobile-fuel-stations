import asyncio

import pytest

from mobile_fuel_stations.const import CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, create_provider
from mobile_fuel_stations.providers.base import (
    ProviderDisabledError,
    StationSearchQuery,
    UnknownProviderError,
)
from mobile_fuel_stations.providers.tankerkoenig import TankerkoenigProvider


class FakeResponse:
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def raise_for_status(self):
        return None

    async def json(self, content_type=None):
        return {"ok": True, "status": "ok", "stations": []}


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        return FakeResponse()


def test_legacy_config_defaults_to_tankerkoenig_provider():
    provider = create_provider(object(), {"api_key": "legacy-secret"})

    assert isinstance(provider, TankerkoenigProvider)


def test_explicit_tankerkoenig_mode_uses_same_provider():
    provider = create_provider(
        object(), {"api_key": "secret", CONF_PROVIDER_MODE: PROVIDER_TANKERKOENIG}
    )

    assert isinstance(provider, TankerkoenigProvider)


def test_unactivated_provider_mode_fails_without_network_access():
    session = FakeSession()
    with pytest.raises(ProviderDisabledError):
        create_provider(session, {"api_key": "secret", CONF_PROVIDER_MODE: "petromap"})
    assert session.calls == []


def test_unknown_provider_mode_fails_before_network_access():
    session = FakeSession()
    with pytest.raises(UnknownProviderError):
        create_provider(session, {"api_key": "secret", CONF_PROVIDER_MODE: "unknown"})
    assert session.calls == []


def test_disabled_registry_entries_have_no_factory():
    assert PROVIDER_REGISTRY["petromap"].enabled is False
    assert PROVIDER_REGISTRY["petromap"].factory is None


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
