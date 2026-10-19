import asyncio

import pytest

from mobile_fuel_stations.const import CONF_NAKORDONI_API_KEY, CONF_PROVIDER_MODE, PROVIDER_NAKORDONI
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, create_provider
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderConfigurationError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderRequestDiagnostics,
    ProviderUnavailableError,
    ProviderUnsupportedFuelError,
    StationSearchQuery,
)
from mobile_fuel_stations.api import station_attributes
from mobile_fuel_stations.providers.nakordoni import (
    NAKORDONI_ACCOUNT_USAGE_URL,
    NakordoniProvider,
    NAKORDONI_API_URL,
)


class Response:
    def __init__(self, payload, status=200, headers=None):
        self.status = status
        self.payload = payload
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def json(self, content_type=None):
        return self.payload


class RequestContextManager:
    """Model aiohttp's ``ClientSession.get`` return value."""

    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return await self._response.__aenter__()

    async def __aexit__(self, *args):
        return await self._response.__aexit__(*args)


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, *, params, headers, timeout):
        self.calls.append((url, params, headers, timeout))
        return RequestContextManager(self.response)


class OAuthSession:
    def __init__(self, response):
        self.response = response

    async def async_request(self, method, url, *, params, timeout):
        return self.response


def payload():
    return {
        "ok": True,
        "data": {
            "count": 1,
            "total_found": 1,
            "stations": [{
                "station_ref": "stable-ref",
                "id": None,
                "name": "Test Station",
                "brand": None,
                "address": {"street": "Example Street", "city": "Saarbrücken"},
                "lat": 49.24,
                "lng": 6.99,
                "distance_km": 1.2,
                "prices": {"diesel": {
                    "price": 1.799,
                    "currency": "EUR",
                    "updated_at": "2026-10-06T20:00:00Z",
                    "confirmed_at": "2026-10-06T20:30:00Z",
                    "age_hours": 0.5,
                    "stale": False,
                }},
            }],
        },
    }


def usage_payload():
    return {
        "ok": True,
        "api_version": "v2",
        "product": "account-usage",
        "data": {
            "plan": {"slug": "explorer", "name": "Explorer"},
            "qps": 2,
            "quotas": {
                "cheap": {"limit": 1000, "used": 42, "remaining": 958, "reset_at": "2026-10-20T00:00:00Z"},
                "heavy": {"limit": 200, "used": 3, "remaining": 197, "reset_at": "2026-10-20T00:00:00Z"},
                "route": {"limit": 10, "used": 0, "remaining": 10, "reset_at": "2026-10-20T00:00:00Z"},
            },
            "markets": {"approved": ["DE"], "allowed": 1, "available": ["AT"], "key_bound": True},
            "pass": {"active": True, "expires_at": "2026-10-22T14:05:00Z", "days_left": 3},
            "upgrade_url": "https://nakordoni.eu/en/developers/billing",
            "pass_url": "https://nakordoni.eu/en/developers/billing?section=trip-pass#trip-pass",
        },
    }


def query():
    return StationSearchQuery(49.24, 6.99, 25, "diesel", station_count=10)


def test_registry_and_factory_are_enabled_without_network():
    session = Session(Response(payload()))
    provider = create_provider(session, {
        CONF_PROVIDER_MODE: PROVIDER_NAKORDONI,
        CONF_NAKORDONI_API_KEY: "nakordoni-dummy",
    })
    assert isinstance(provider, NakordoniProvider)
    assert PROVIDER_REGISTRY[PROVIDER_NAKORDONI].enabled is True
    assert session.calls == []


def test_nakordoni_never_falls_back_to_generic_legacy_key():
    with pytest.raises(ProviderConfigurationError):
        create_provider(Session(Response(payload())), {
            CONF_PROVIDER_MODE: PROVIDER_NAKORDONI,
            "api_key": "legacy-tankerkoenig-dummy",
        })


def test_nakordoni_request_uses_bearer_header_and_one_page():
    session = Session(Response(payload(), headers={"X-Devapi-Limit": "1000", "X-Devapi-Remaining": "999"}))
    provider = NakordoniProvider(session, "nakordoni-dummy")
    stations = asyncio.run(provider.async_search(query()))
    url, params, headers, _ = session.calls[0]
    assert len(session.calls) == 1
    assert url == NAKORDONI_API_URL
    assert params == {"lat": "49.2400000", "lon": "6.9900000", "radius_km": "25", "fuel_type": "diesel", "limit": "10", "lang": "de"}
    assert headers == {"Authorization": "Bearer nakordoni-dummy"}
    assert stations[0].station_id == "stable-ref"
    assert stations[0].brand == ""
    assert stations[0].price == 1.799
    assert stations[0].price_stale is False
    assert provider.last_response_metadata.quota_remaining == 999
    assert station_attributes(stations[0])["currency"] == "EUR"
    assert station_attributes(stations[0])["price_age_hours"] == 0.5


def test_nakordoni_binds_aiohttp_request_context_to_response():
    """Regression: aiohttp exposes headers/status only after ``__aenter__``."""

    provider = NakordoniProvider(Session(Response(payload())), "dummy")

    stations = asyncio.run(provider.async_search(query()))

    assert len(stations) == 1


def test_nakordoni_oauth_response_remains_supported():
    provider = NakordoniProvider(
        Session(Response(payload())),
        None,
        oauth_session=OAuthSession(Response(payload())),
    )

    stations = asyncio.run(provider.async_search(query()))

    assert len(stations) == 1


def test_nakordoni_account_usage_uses_documented_shape_without_station_params():
    session = Session(Response(usage_payload()))
    provider = NakordoniProvider(session, "dummy")

    usage = asyncio.run(provider.async_get_account_usage())

    url, params, headers, _ = session.calls[0]
    assert url == NAKORDONI_ACCOUNT_USAGE_URL
    assert params == {}
    assert headers == {"Authorization": "Bearer dummy"}
    assert usage.plan_slug == "explorer"
    assert usage.cheap.remaining == 958
    assert usage.cheap.reset_at.isoformat() == "2026-10-20T00:00:00+00:00"
    assert usage.markets_approved == ("DE",)
    assert usage.markets_allowed == 1
    assert usage.pass_active is True
    assert usage.pass_days_left == 3
    assert usage.as_diagnostics()["quotas"]["route"]["remaining"] == 10


def test_nakordoni_account_usage_preserves_product_permission_error():
    provider = NakordoniProvider(Session(Response({
        "ok": False,
        "error": {
            "code": "integration_product_not_allowed",
            "upgrade_url": "https://example.invalid/upgrade",
            "pass_url": "https://example.invalid/pass",
        },
    }, status=403)), "dummy")

    with pytest.raises(ProviderPermissionError) as caught:
        asyncio.run(provider.async_get_account_usage())

    assert caught.value.diagnostics.error_code == "integration_product_not_allowed"
    assert caught.value.upgrade_url == "https://example.invalid/upgrade"
    assert caught.value.pass_url == "https://example.invalid/pass"


@pytest.mark.parametrize("status, error_type", [(401, ProviderAuthError), (403, ProviderPermissionError), (429, ProviderRateLimitError)])
def test_nakordoni_http_errors_are_classified(status, error_type):
    provider = NakordoniProvider(Session(Response({"ok": False, "error": {"code": "provider_error"}}, status=status)), "dummy")
    with pytest.raises(error_type):
        asyncio.run(provider.async_search(query()))


def test_nakordoni_rate_failure_preserves_only_safe_metadata():
    session = Session(Response(
        {"ok": False, "error": {"code": "qps_exceeded", "message": "do not expose"}},
        status=429,
        headers={"Retry-After": "60", "X-Devapi-Limit": "1000", "X-Devapi-Remaining": "999"},
    ))
    provider = NakordoniProvider(session, "SECRET_MUST_NOT_APPEAR")

    with pytest.raises(ProviderRateLimitError) as caught:
        asyncio.run(provider.async_search(query()))

    diagnostics = caught.value.diagnostics
    assert isinstance(diagnostics, ProviderRequestDiagnostics)
    assert diagnostics.as_dict() == {
        "provider": "nakordoni",
        "http_status": 429,
        "error_code": "qps_exceeded",
        "retry_after": 60,
        "quota_limit": 1000,
        "quota_remaining": 999,
        "request_success": False,
        "response_ok": False,
    }
    assert "SECRET_MUST_NOT_APPEAR" not in repr(diagnostics)
    assert "do not expose" not in repr(diagnostics)


def test_nakordoni_unknown_error_code_is_redacted():
    provider = NakordoniProvider(Session(Response(
        {"ok": False, "error": {"code": "private-provider-detail"}}, status=403,
    )), "dummy")

    with pytest.raises(ProviderPermissionError) as caught:
        asyncio.run(provider.async_search(query()))

    assert caught.value.diagnostics.error_code == "provider_error"


@pytest.mark.parametrize(
    ("status", "code", "error_type"),
    [
        (429, "quota_exceeded", ProviderRateLimitError),
        (403, "market_not_allowed", ProviderPermissionError),
        (403, "not_approved", ProviderPermissionError),
        (401, "invalid_credential", ProviderAuthError),
    ],
)
def test_nakordoni_known_error_codes_are_preserved(status, code, error_type):
    provider = NakordoniProvider(Session(Response(
        {"ok": False, "error": {"code": code}}, status=status,
        headers={"Retry-After": "-1", "X-Devapi-Limit": "invalid", "X-Devapi-Remaining": "-2"},
    )), "dummy")

    with pytest.raises(error_type) as caught:
        asyncio.run(provider.async_search(query()))

    diagnostics = caught.value.diagnostics
    assert diagnostics.error_code == code
    assert diagnostics.retry_after is None
    assert diagnostics.quota_limit is None
    assert diagnostics.quota_remaining is None


def test_nakordoni_server_failure_has_safe_diagnostics():
    provider = NakordoniProvider(Session(Response(
        {"ok": False, "error": {"code": "internal_error", "message": "private"}}, status=503,
    )), "dummy")

    with pytest.raises(ProviderUnavailableError) as caught:
        asyncio.run(provider.async_search(query()))

    assert caught.value.diagnostics.http_status == 503
    assert caught.value.diagnostics.error_code == "provider_error"
    assert "private" not in repr(caught.value.diagnostics)


def test_nakordoni_success_then_failure_does_not_retain_success_metadata():
    session = Session(Response(payload(), headers={"X-Devapi-Limit": "1000", "X-Devapi-Remaining": "999"}))
    provider = NakordoniProvider(session, "dummy")
    asyncio.run(provider.async_search(query()))
    session.response = Response(
        {"ok": False, "error": {"code": "quota_exceeded"}}, status=429,
    )

    with pytest.raises(ProviderRateLimitError):
        asyncio.run(provider.async_search(query()))

    assert provider.last_response_metadata is None
    assert provider.last_request_diagnostics.quota_limit is None
    assert provider.last_request_diagnostics.error_code == "quota_exceeded"


def test_nakordoni_rejects_unverified_fuels_without_network():
    session = Session(Response(payload()))
    provider = NakordoniProvider(session, "dummy")
    with pytest.raises(ProviderUnsupportedFuelError, match="not verified"):
        asyncio.run(provider.async_search(StationSearchQuery(49.24, 6.99, 25, "hvo100")))
    assert session.calls == []
