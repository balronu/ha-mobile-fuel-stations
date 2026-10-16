"""Administrator-only, non-mutating Nakordoni diagnostics."""

from __future__ import annotations

import asyncio
from time import monotonic
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_NAKORDONI_API_KEY,
    CONF_NAKORDONI_AUTH_METHOD,
    CONF_PROVIDER_MODES,
    CONF_PROVIDER_MODE,
    DOMAIN,
    PROVIDER_NAKORDONI,
)
from .providers.nakordoni import NAKORDONI_FUELS, NakordoniProvider
from .providers.base import ProviderError, ProviderRequestDiagnostics, StationSearchQuery

MAX_PROBE_CALLS = 3
_MAX_STATION_COUNT = 20


def _validate(
    latitude: object,
    longitude: object,
    radius_km: object,
    fuel_type: object,
    station_count: object,
) -> tuple[float, float, float, str, int]:
    if isinstance(latitude, bool) or not isinstance(latitude, (int, float)):
        raise ValueError("latitude must be numeric")
    if isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
        raise ValueError("longitude must be numeric")
    if isinstance(radius_km, bool) or not isinstance(radius_km, (int, float)):
        raise ValueError("radius_km must be numeric")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("coordinates are outside WGS84 bounds")
    if not 0 < radius_km <= 25:
        raise ValueError("radius_km must be greater than 0 and at most 25")
    if not isinstance(fuel_type, str) or fuel_type not in NAKORDONI_FUELS:
        raise ValueError("fuel_type is not verified for Nakordoni")
    if isinstance(station_count, bool) or not isinstance(station_count, int):
        raise ValueError("station_count must be an integer")
    if not 1 <= station_count <= _MAX_STATION_COUNT:
        raise ValueError("station_count must be between 1 and 20")
    return float(latitude), float(longitude), float(radius_km), fuel_type, station_count


def _configured_for_nakordoni(entry: ConfigEntry) -> bool:
    config = {**entry.data, **entry.options}
    modes = config.get(CONF_PROVIDER_MODES)
    return config.get(CONF_PROVIDER_MODE) == PROVIDER_NAKORDONI or (
        isinstance(modes, (list, tuple, set)) and PROVIDER_NAKORDONI in modes
    )


def _diagnostics(provider: Any) -> ProviderRequestDiagnostics | None:
    value = getattr(provider, "last_request_diagnostics", None)
    return value if isinstance(value, ProviderRequestDiagnostics) else None


def _safe_error(error: Exception) -> str:
    diagnostics = getattr(error, "diagnostics", None)
    code = getattr(diagnostics, "error_code", None)
    return code if isinstance(code, str) else "provider_error"


def _result(
    *,
    fuel_type: str,
    radius_km: float,
    elapsed_ms: int,
    stations: list[Any],
    provider: Any,
    error_code: str | None = None,
) -> dict[str, object]:
    diagnostics = _diagnostics(provider)
    priced = [station for station in stations if station.price is not None]
    ages = [station.price_age_hours for station in priced if station.price_age_hours is not None]
    updated = [station.price_updated_at for station in priced if station.price_updated_at is not None]
    metadata = getattr(provider, "last_response_metadata", None)
    output: dict[str, object] = {
        "provider": PROVIDER_NAKORDONI,
        "fuel_type": fuel_type,
        "radius_km": radius_km,
        "http_status": diagnostics.http_status if diagnostics else None,
        "response_ok": diagnostics.response_ok if diagnostics else None,
        "request_success": diagnostics.request_success if diagnostics else False,
        "error_code": error_code or (diagnostics.error_code if diagnostics else None),
        "retry_after": diagnostics.retry_after if diagnostics else None,
        "quota_limit": diagnostics.quota_limit if diagnostics else None,
        "quota_remaining": diagnostics.quota_remaining if diagnostics else None,
        "latency_ms": elapsed_ms,
        "station_count": len(stations),
        "priced_station_count": len(priced),
        "price_coverage_percent": round(len(priced) * 100 / len(stations), 1) if stations else 0.0,
        "price_age_hours_min": min(ages) if ages else None,
        "price_age_hours_max": max(ages) if ages else None,
        "latest_price_updated_at": max(updated).isoformat() if updated else None,
        "empty_reason": getattr(metadata, "empty_reason", None) if not stations else None,
        "nearest_station_km": getattr(metadata, "nearest_station_km", None) if not stations else None,
    }
    return output


async def async_probe_nakordoni(
    hass: HomeAssistant,
    entry: ConfigEntry,
    latitude: object,
    longitude: object,
    radius_km: object,
    fuel_type: object,
    *,
    station_count: object = _MAX_STATION_COUNT,
    provider: Any | None = None,
) -> dict[str, object]:
    """Run exactly one direct Nakordoni request without touching coordinator state."""

    latitude, longitude, radius_km, fuel_type, station_count = _validate(
        latitude, longitude, radius_km, fuel_type, station_count
    )
    if not _configured_for_nakordoni(entry):
        raise ValueError("Nakordoni is not configured for this entry")

    config = {**entry.data, **entry.options}
    if provider is None:
        session = async_get_clientsession(hass)
        oauth_session = None
        auth_method = config.get(CONF_NAKORDONI_AUTH_METHOD, "api_key")
        if auth_method == "oauth2":
            from homeassistant.helpers.config_entry_oauth2_flow import (
                OAuth2Session,
                async_get_config_entry_implementation,
            )

            implementation = await async_get_config_entry_implementation(hass, entry)
            oauth_session = OAuth2Session(hass, entry, implementation)
        elif auth_method != "api_key":
            raise ValueError("Unsupported Nakordoni authentication method")
        elif not isinstance(config.get(CONF_NAKORDONI_API_KEY), str) or not config[CONF_NAKORDONI_API_KEY].strip():
            raise ValueError("Nakordoni API key is not configured")
        provider = NakordoniProvider(
            session,
            config.get(CONF_NAKORDONI_API_KEY),
            oauth_session=oauth_session,
        )

    started = monotonic()
    try:
        stations = await provider.async_search(
            StationSearchQuery(latitude, longitude, radius_km, fuel_type, station_count)
        )
    except ProviderError as error:
        return _result(
            fuel_type=fuel_type,
            radius_km=radius_km,
            elapsed_ms=round((monotonic() - started) * 1000),
            stations=[],
            provider=provider,
            error_code=_safe_error(error),
        )
    return _result(
        fuel_type=fuel_type,
        radius_km=radius_km,
        elapsed_ms=round((monotonic() - started) * 1000),
        stations=stations,
        provider=provider,
    )


async def async_register_probe_service(hass: HomeAssistant) -> None:
    """Register the authenticated, administrator-only probe service once."""

    from homeassistant.exceptions import HomeAssistantError
    from homeassistant.helpers import config_validation as cv
    import voluptuous as vol

    async def handle(call: ServiceCall) -> dict[str, object]:
        user_id = call.context.user_id
        user = await hass.auth.async_get_user(user_id) if user_id else None
        if user is None or not user.is_admin:
            raise HomeAssistantError("Administrator permission is required")
        entry_id = call.data.get("config_entry_id", call.data.get("entry_id"))
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            raise HomeAssistantError("Mobile Fuel Stations config entry not found")
        locks = hass.data.setdefault(DOMAIN, {}).setdefault("probe_locks", {})
        lock = locks.setdefault(entry.entry_id, asyncio.Lock())
        if lock.locked():
            raise HomeAssistantError("A Nakordoni diagnostic is already running")
        async with lock:
            return await async_probe_nakordoni(
                hass,
                entry,
                call.data["latitude"],
                call.data["longitude"],
                call.data["radius_km"],
                call.data["fuel_type"],
                station_count=call.data.get("station_count", _MAX_STATION_COUNT),
            )

    schema = vol.Schema({
        vol.Required("entry_id"): cv.string,
        vol.Required("latitude"): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)),
        vol.Required("longitude"): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
        vol.Required("radius_km"): vol.All(vol.Coerce(float), vol.Range(min=0.001, max=25)),
        vol.Required("fuel_type"): vol.In(sorted(NAKORDONI_FUELS)),
        vol.Optional("station_count", default=_MAX_STATION_COUNT): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
    })
    hass.services.async_register(
        DOMAIN,
        "probe_nakordoni",
        handle,
        schema=schema,
        supports_response=SupportsResponse.ONLY,
    )


__all__ = ["MAX_PROBE_CALLS", "async_probe_nakordoni", "async_register_probe_service"]
