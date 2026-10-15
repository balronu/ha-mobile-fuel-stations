"""Coordinator with persistent successful-search state and movement refreshes."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, replace
import json
import logging
from math import asin, cos, isfinite, radians, sin, sqrt
import random
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry, ConfigEntryAuthFailed
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_state_report_event,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import Station, cheapest_by_fuel, nearest_station, sort_stations, merge_stations
from .const import (
    CONF_COOLDOWN,
    CONF_ADAPTIVE_UPDATES,
    CONF_FUEL_TYPE,
    CONF_FUEL_TYPES,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_UPDATE_INTERVAL,
    CONF_PROVIDER_MODE,
    CONF_PROVIDER_MODES,
    CONF_SORT_FUEL,
    CONF_SORT_MODE,
    DEFAULT_SORT_FUEL,
    DEFAULT_SORT_MODE,
    DEFAULT_ADAPTIVE_MOVEMENT_THRESHOLD_KM,
    ADAPTIVE_CITY_INTERVAL,
    ADAPTIVE_COUNTRY_ROAD_INTERVAL,
    ADAPTIVE_MOTORWAY_INTERVAL,
    ADAPTIVE_STATIONARY_INTERVAL,
    DOMAIN,
    MAX_API_RADIUS_KM,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
    PROVIDER_NAKORDONI,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .providers import create_provider
from .providers.base import (
    CountryPriceCoverage,
    FuelFallbackBlockedError,
    NoSuitableProviderError,
    ProviderAuthError,
    ProviderError,
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderRequestDiagnostics,
    ProviderResponseError,
    ProviderReauthContext,
    ProviderUnsupportedFuelError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    StationSearchQuery,
    resolve_fuel,
)
from .providers import PROVIDER_REGISTRY
from .providers.policy import (
    AutoProviderDecision,
    AutoRuntimeState,
    CountryHysteresis,
    choose_auto_provider,
    validate_direct_fuel_runtime,
)
from .country_resolver import resolve

_LOGGER = logging.getLogger(__name__)
_TRANSIENT_PROVIDER_ERRORS = (
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
_MAX_RETRY_AFTER_SECONDS = 3600
_STARTUP_RECOVERY_DELAYS = (3.0, 10.0, 30.0)
_STARTUP_RECOVERY_SLOW_INTERVAL = 60.0
_RECOVERY_BACKOFF_BASE = 5.0
_RECOVERY_BACKOFF_CAP = 300.0
_MAX_GPS_AGE = timedelta(minutes=10)
_MAX_GPS_ACCURACY_METERS = 1000.0
_MAX_PLAUSIBLE_SPEED_KMH = 200.0
_MIN_PROVIDER_INTERVALS = {
    PROVIDER_TANKERKOENIG: timedelta(minutes=5),
}
_STATION_CACHE_KEY = "stations"
_CACHE_CONTEXT_KEY = "station_cache_context"


@dataclass(slots=True, frozen=True)
class GpsSample:
    """Validated tracker position used for adaptive scheduling."""

    position: tuple[float, float]
    observed_at: datetime
    accuracy_m: float | None
    speed_kmh: float | None


def _state_timestamp(state: Any) -> datetime | None:
    """Return the freshest HA state timestamp available on a test/live state."""

    for name in ("last_reported", "last_updated", "last_changed"):
        value = getattr(state, name, None)
        if isinstance(value, datetime):
            return value if value.tzinfo else value.astimezone()
    return None


def _numeric_attribute(attributes: dict[str, Any], *names: str) -> float | None:
    for name in names:
        value = attributes.get(name)
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            continue
        if isfinite(parsed):
            return parsed
    return None


def _gps_sample(
    hass: HomeAssistant,
    entity_id: str,
    *,
    now: datetime | None = None,
    previous: GpsSample | None = None,
) -> GpsSample | None:
    """Read and validate one tracker sample without logging private coordinates."""

    states = getattr(hass, "states", None)
    if states is None:
        return None
    state = states.get(entity_id)
    if state is None or state.state in ("unknown", "unavailable"):
        return None
    attributes = getattr(state, "attributes", {})
    try:
        latitude = float(attributes.get("latitude"))
        longitude = float(attributes.get("longitude"))
    except (TypeError, ValueError):
        return None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    accuracy = _numeric_attribute(attributes, "gps_accuracy", "accuracy")
    if accuracy is not None and (accuracy < 0 or accuracy > _MAX_GPS_ACCURACY_METERS):
        return None
    observed_at = _state_timestamp(state) or now or datetime.now().astimezone()
    current = now or datetime.now().astimezone()
    age = (current - observed_at).total_seconds()
    if age < -30 or age > _MAX_GPS_AGE.total_seconds():
        return None
    speed = _numeric_attribute(attributes, "speed_kmh", "speed", "velocity")
    unit = str(attributes.get("speed_unit", "km/h")).lower()
    if speed is not None and "mph" in unit:
        speed *= 1.609344
    if speed is not None and (speed < 0 or speed > _MAX_PLAUSIBLE_SPEED_KMH):
        speed = None
    sample = GpsSample((latitude, longitude), observed_at, accuracy, speed)
    if sample.speed_kmh is None and previous is not None:
        elapsed = (sample.observed_at - previous.observed_at).total_seconds()
        if elapsed >= 5:
            derived = haversine_km(previous.position, sample.position) / (elapsed / 3600)
            if isfinite(derived) and 0 <= derived <= _MAX_PLAUSIBLE_SPEED_KMH:
                sample = replace(sample, speed_kmh=derived)
    return sample


def _retry_after_seconds(error: ProviderError) -> int | None:
    """Read a bounded, provider-neutral Retry-After value."""

    diagnostics = getattr(error, "diagnostics", None)
    value = getattr(diagnostics, "retry_after", None)
    if value is None:
        value = getattr(error, "retry_after", None)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return min(parsed, _MAX_RETRY_AFTER_SECONDS) if parsed >= 0 else None


def _valid_position(hass: HomeAssistant, entity_id: str) -> tuple[float, float] | None:
    state = hass.states.get(entity_id)
    if state is None or state.state in ("unknown", "unavailable"):
        return None
    try:
        latitude = float(state.attributes.get("latitude"))
        longitude = float(state.attributes.get("longitude"))
    except (TypeError, ValueError):
        return None
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return None
    return latitude, longitude


def haversine_km(first: tuple[float, float], second: tuple[float, float]) -> float:
    """Return geodesic distance between two WGS84 coordinate pairs."""

    lat1, lon1 = map(radians, first)
    lat2, lon2 = map(radians, second)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(a))


class CountryAutoContext:
    """Prepare country/provider context without changing the active provider."""

    def __init__(
        self,
        fuel_type: str,
        resolver: Callable[[float, float], str | None] = resolve,
        allowed_providers: set[str] | frozenset[str] | None = None,
    ) -> None:
        self.fuel_type = fuel_type
        self._resolver = resolver
        self.allowed_providers = frozenset(allowed_providers or {
            PROVIDER_TANKERKOENIG,
            PROVIDER_PETROMAP,
            PROVIDER_NAKORDONI,
        })
        self._hysteresis = CountryHysteresis()
        self.raw_country: str | None = None
        self.confirmed_country: str | None = None
        self.auto_provider_decision: AutoProviderDecision | None = None

    def observe_position(self, position: tuple[float, float]) -> AutoProviderDecision:
        """Resolve one relevant GPS position and evaluate the offline policy."""

        try:
            self.raw_country = self._resolver(position[0], position[1])
        except (OSError, json.JSONDecodeError, KeyError) as err:
            _LOGGER.warning("Offline country resolver unavailable (%s)", type(err).__name__)
            self.raw_country = None
        self.confirmed_country = self._hysteresis.observe(self.raw_country)
        tankerkoenig = PROVIDER_REGISTRY[PROVIDER_TANKERKOENIG]
        petromap = PROVIDER_REGISTRY[PROVIDER_PETROMAP]
        nakordoni = PROVIDER_REGISTRY[PROVIDER_NAKORDONI]
        self.auto_provider_decision = choose_auto_provider(
            self.confirmed_country,
            self.fuel_type,
            tankerkoenig_enabled=tankerkoenig.enabled and PROVIDER_TANKERKOENIG in self.allowed_providers,
            tankerkoenig_capabilities=tankerkoenig.capabilities,
            petromap_enabled=petromap.enabled and PROVIDER_PETROMAP in self.allowed_providers,
            petromap_capabilities=petromap.capabilities,
            nakordoni_enabled=nakordoni.enabled and PROVIDER_NAKORDONI in self.allowed_providers,
            nakordoni_capabilities=nakordoni.capabilities,
        )
        return self.auto_provider_decision


class MobileFuelStationsCoordinator(DataUpdateCoordinator[list[Station] | None]):
    """Fetch and retain nearby stations."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.options = {**entry.data, **entry.options}
        interval = int(self.options[CONF_UPDATE_INTERVAL])
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval),
            config_entry=entry,
        )
        self._session = async_get_clientsession(hass)
        self._providers: dict[str, Any] = {}
        self.client = None
        if self.options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG) != "auto":
            provider_mode = self.options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            key_name = {
                PROVIDER_TANKERKOENIG: "tankerkoenig_api_key",
                PROVIDER_PETROMAP: "petromap_api_key",
                PROVIDER_NAKORDONI: "nakordoni_api_key",
            }.get(provider_mode)
            if key_name and self.options.get(key_name):
                self.client = create_provider(self._session, self.options)
        self.stations: list[Station] = []
        self.nearest_station: Station | None = None
        self.cheapest_station: Station | None = None
        self.cheapest_stations: dict[str, Station] = {}
        self.last_successful_update: datetime | None = None
        self.reference_position: tuple[float, float] | None = None
        self.last_gps_sample: GpsSample | None = None
        self._last_gps_event_key: tuple[float, float, datetime] | None = None
        self.last_request: datetime | None = None
        self.last_update_attempt: datetime | None = None
        self.last_update_result: str | None = None
        self.last_provider_attempt: datetime | None = None
        self.last_provider_success: datetime | None = None
        self.last_update_error_at: datetime | None = None
        self.last_update_error_class: str | None = None
        self.last_update_error_provider: str | None = None
        self.last_retry_after: int | None = None
        self.data_stale = False
        self.recovery_status = "never"
        self.consecutive_failures = 0
        self._retry_not_before: datetime | None = None
        self._unsub_position = None
        self._unsub_position_report = None
        self.gps_listener_registered = False
        self._movement_refresh_scheduled = False
        self._movement_refresh_task: asyncio.Task | None = None
        self.recovery_task_status = "not_scheduled"
        self.recovery_attempt_count = 0
        self.recovery_trigger: str | None = None
        self.recovery_next_retry_at: datetime | None = None
        self.recovery_last_gps_event_type: str | None = None
        self.recovery_last_gps_event_at: datetime | None = None
        self.recovery_provider_in_flight = False
        self.recovery_error_class: str | None = None
        self._recovery_timer_unsub = None
        self._recovery_active = False
        self._recovery_started_at: datetime | None = datetime.now().astimezone()
        self._recovery_startup_index = 0
        self._recovery_transient_failures = 0
        self._recovery_task: asyncio.Task | None = None
        self._recovery_request_scheduled = False
        self._cooldown_timer_unsub = None
        self._cooldown_refresh_task: asyncio.Task | None = None
        self._provider_lock: asyncio.Lock | None = None
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry.entry_id}")
        self._provider_status_store = Store(hass, 1, f"{DOMAIN}.provider_status.{entry.entry_id}")
        # Keep the status in the runtime object as well as hass.data.  The
        # options flow can be opened while the integration is being reloaded;
        # reading the runtime copy avoids a transient "untested" display when
        # the persisted result has already been loaded for this coordinator.
        self.provider_status: dict[str, dict[str, str]] = {}
        self.fuel_types = self._configured_fuels(self.options)
        self.provider_modes = self._configured_provider_modes(self.options)
        self.available_provider_modes = frozenset(
            provider
            for provider in self.provider_modes
            if self.options.get({
                PROVIDER_TANKERKOENIG: "tankerkoenig_api_key",
                PROVIDER_PETROMAP: "petromap_api_key",
                PROVIDER_NAKORDONI: "nakordoni_api_key",
            }[provider])
        )
        self.country_auto_context = CountryAutoContext(
            self.fuel_types[0], allowed_providers=self.available_provider_modes
        )
        self.auto_runtime_state: AutoRuntimeState | None = None

    @property
    def _is_auto(self) -> bool:
        return self.options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG) == "auto"

    @staticmethod
    def _configured_fuels(options: dict[str, Any]) -> list[str]:
        raw = options.get(CONF_FUEL_TYPES, options.get(CONF_FUEL_TYPE, "diesel"))
        values = [raw] if isinstance(raw, str) else raw if isinstance(raw, (list, tuple, set)) else []
        fuels: list[str] = []
        for fuel in values:
            if isinstance(fuel, str) and fuel in {"e5", "e10", "diesel", "lpg", "hvo100"} and fuel not in fuels:
                fuels.append(fuel)
        return fuels or ["diesel"]

    @staticmethod
    def _configured_provider_modes(options: dict[str, Any]) -> frozenset[str]:
        raw = options.get(CONF_PROVIDER_MODES)
        if isinstance(raw, str):
            values = [raw]
        elif isinstance(raw, (list, tuple, set, frozenset)):
            values = list(raw)
        else:
            mode = options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            values = [mode] if mode != "auto" else [
                PROVIDER_TANKERKOENIG,
                PROVIDER_PETROMAP,
                PROVIDER_NAKORDONI,
            ]
        return frozenset(value for value in values if value in {
            PROVIDER_TANKERKOENIG,
            PROVIDER_PETROMAP,
            PROVIDER_NAKORDONI,
        }) or frozenset({PROVIDER_TANKERKOENIG})

    def _get_provider(self, provider_mode: str):
        """Return one cached concrete provider for Auto runtime."""

        if provider_mode not in (PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP, PROVIDER_NAKORDONI):
            raise ValueError(f"Auto selected non-concrete provider: {provider_mode}")
        provider = self._providers.get(provider_mode)
        if provider is not None:
            return provider
        registration = PROVIDER_REGISTRY[provider_mode]
        key_name = {
            PROVIDER_TANKERKOENIG: "tankerkoenig_api_key",
            PROVIDER_PETROMAP: "petromap_api_key",
            PROVIDER_NAKORDONI: "nakordoni_api_key",
        }[provider_mode]
        provider = registration.factory(self._session, self.options[key_name])
        self._providers[provider_mode] = provider
        return provider

    def _record_nakordoni_failure(self, error: ProviderError) -> None:
        """Publish only approved Nakordoni diagnostics before setup can fail."""

        diagnostics = getattr(error, "diagnostics", None)
        if not isinstance(diagnostics, ProviderRequestDiagnostics):
            return
        domain_data = self.hass.data.setdefault(DOMAIN, {})
        records = domain_data.setdefault("last_request_diagnostics", {})
        records[self.entry.entry_id] = diagnostics.as_dict()
        fields = [
            f"status={diagnostics.http_status}",
            f"code={diagnostics.error_code}",
            f"retry_after={diagnostics.retry_after}",
            f"quota_limit={diagnostics.quota_limit}",
            f"quota_remaining={diagnostics.quota_remaining}",
        ]
        _LOGGER.warning("Nakordoni request failed: %s", " ".join(fields))

    def _record_nakordoni_success(self, provider: Any) -> None:
        """Publish the latest safe success metadata for a loaded entry."""

        diagnostics = getattr(provider, "last_request_diagnostics", None)
        if not isinstance(diagnostics, ProviderRequestDiagnostics):
            return
        self.hass.data.setdefault(DOMAIN, {}).setdefault(
            "last_request_diagnostics", {}
        )[self.entry.entry_id] = diagnostics.as_dict()

    def _nakordoni_error_message(self, error: ProviderError) -> str:
        """Return a bounded, provider-specific message without raw response text."""

        code = getattr(getattr(error, "diagnostics", None), "error_code", None)
        return {
            "qps_exceeded": "Nakordoni rate limit reached: qps_exceeded",
            "quota_exceeded": "Nakordoni quota exceeded",
            "market_not_allowed": "Nakordoni market not allowed",
            "not_approved": "Nakordoni account/product not approved",
        }.get(code, "nakordoni request failed")

    def _set_auto_runtime_state(
        self,
        decision: AutoProviderDecision,
        *,
        effective_provider: str | None = None,
        reason: str | None = None,
    ) -> None:
        previous = getattr(self, "auto_runtime_state", None)
        if (
            effective_provider is None
            and decision.reason != "location_unavailable"
            and previous is not None
        ):
            # A provider cooldown can defer the newly selected provider.  Keep
            # reporting the provider that is actually effective until a new
            # request succeeds; do not briefly expose ``None``.
            effective_provider = previous.effective_provider
        self.auto_runtime_state = AutoRuntimeState(
            configured_provider_mode="auto",
            effective_provider=effective_provider,
            raw_country=self.country_auto_context.raw_country,
            confirmed_country=self.country_auto_context.confirmed_country,
            coverage=decision.coverage,
            fuel_resolution=decision.fuel_resolution,
            reason=reason or decision.reason,
        )

    async def async_setup(self) -> None:
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self.last_successful_update = self._parse_time(stored.get("last_successful_update"))
            self.last_request = self._parse_time(stored.get("last_request"))
            self.last_update_attempt = self._parse_time(stored.get("last_update_attempt"))
            self.last_update_error_at = self._parse_time(stored.get("last_update_error_at"))
            self.last_update_error_class = stored.get("last_update_error_class")
            self.last_update_error_provider = stored.get("last_update_error_provider")
            self.last_retry_after = stored.get("last_retry_after")
            self.data_stale = bool(stored.get("data_stale", False))
            self.recovery_status = str(stored.get("recovery_status", "never"))
            self.consecutive_failures = int(stored.get("consecutive_failures", 0))
            lat, lon = stored.get("reference_latitude"), stored.get("reference_longitude")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                self.reference_position = (float(lat), float(lon))
            gps_lat, gps_lon = stored.get("last_gps_latitude"), stored.get("last_gps_longitude")
            gps_at = self._parse_time(stored.get("last_gps_at"))
            if (
                isinstance(gps_lat, (int, float))
                and isinstance(gps_lon, (int, float))
                and gps_at is not None
            ):
                self.last_gps_sample = GpsSample(
                    (float(gps_lat), float(gps_lon)), gps_at, None, None
                )
            cached = self._load_cached_stations(stored)
            if cached is not None:
                self._set_station_data(cached)
                self.data_stale = True
                # Data loaded from disk is immediately useful, but must be
                # visibly marked stale until a provider refresh succeeds.
                self.data = self.stations
                self._schedule_provider_cooldown_refresh()
        provider_status = await self._provider_status_store.async_load()
        self.provider_status = (
            provider_status if isinstance(provider_status, dict) else {}
        )
        domain_data = self.hass.data.setdefault(DOMAIN, {})
        domain_data.setdefault("provider_status", {})[self.entry.entry_id] = self.provider_status
        if self.options.get(CONF_MOVEMENT_UPDATES, True):
            self._unsub_position = async_track_state_change_event(
                self.hass, [self.options[CONF_LOCATION_ENTITY]], self._async_position_changed
            )
            self._unsub_position_report = async_track_state_report_event(
                self.hass,
                [self.options[CONF_LOCATION_ENTITY]],
                self._async_position_reported,
            )
            self.gps_listener_registered = True

    def _cache_context(self) -> dict[str, object]:
        """Return non-sensitive configuration needed to scope cached results."""

        return {
            "provider_modes": sorted(self.provider_modes),
            "fuel_types": sorted(self.fuel_types),
            "radius": float(self.options[CONF_RADIUS]),
            "station_count": int(self.options[CONF_STATION_COUNT]),
            "sort_mode": self.options.get(CONF_SORT_MODE, DEFAULT_SORT_MODE),
            "sort_fuel": self.options.get(
                CONF_SORT_FUEL,
                self.fuel_types[0] if self.fuel_types else DEFAULT_SORT_FUEL,
            ),
        }

    def _load_cached_stations(self, stored: dict[str, Any]) -> list[Station] | None:
        """Load only a complete cache belonging to this entry and query."""

        context = stored.get(_CACHE_CONTEXT_KEY)
        if not isinstance(context, dict) or context != self._cache_context():
            return None
        raw_stations = stored.get(_STATION_CACHE_KEY)
        if not isinstance(raw_stations, list):
            return None
        stations: list[Station] = []
        try:
            for raw in raw_stations:
                station = self._station_from_store(raw)
                if station is None:
                    return None
                stations.append(station)
        except (TypeError, ValueError):
            return None
        reference = self.reference_position
        current = None
        if getattr(self.hass, "states", None) is not None:
            current = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        if reference is not None and current is not None:
            # Do not silently expose a cache from a different place after a
            # location change. The persisted reference is already part of the
            # existing state payload; no additional GPS data is stored.
            if haversine_km(reference, current) > max(float(self.options[CONF_RADIUS]), 1.0):
                return None
        return stations

    @staticmethod
    def _station_to_store(station: Station) -> dict[str, object]:
        """Serialize the provider-neutral station model without secrets."""

        result = {
            "station_id": station.station_id,
            "name": station.name,
            "brand": station.brand,
            "price": station.price,
            "distance": station.distance,
            "is_open": station.is_open,
            "street": station.street,
            "house_number": station.house_number,
            "postcode": station.postcode,
            "place": station.place,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "currency": station.currency,
            "price_updated_at": station.price_updated_at.isoformat()
            if station.price_updated_at else None,
            "country_code": station.country_code,
            "provider": station.provider,
            "price_confirmed_at": station.price_confirmed_at.isoformat()
            if station.price_confirmed_at else None,
            "price_age_hours": station.price_age_hours,
            "price_stale": station.price_stale,
            "fuel_type": station.fuel_type,
            "requested_fuel": station.requested_fuel,
            "fallback_used": station.fallback_used,
            "fuel_prices": station.fuel_prices,
            "fuel_fallbacks": station.fuel_fallbacks,
        }
        return result

    @classmethod
    def _station_from_store(cls, raw: object) -> Station | None:
        if not isinstance(raw, dict):
            return None
        required = ("station_id", "name", "brand", "street", "house_number", "postcode", "place")
        if any(not isinstance(raw.get(key), str) for key in required):
            return None

        def number(key: str, *, finite: bool = True) -> float | None:
            value = raw.get(key)
            if value is None:
                return None
            parsed = float(value)
            if finite and not isfinite(parsed):
                raise ValueError(key)
            return parsed

        def timestamp(key: str) -> datetime | None:
            value = raw.get(key)
            if value is None:
                return None
            parsed = cls._parse_time(value)
            if parsed is None:
                raise ValueError(key)
            return parsed

        latitude, longitude = number("latitude"), number("longitude")
        if latitude is not None and not -90 <= latitude <= 90:
            return None
        if longitude is not None and not -180 <= longitude <= 180:
            return None
        is_open = raw.get("is_open")
        if is_open is not None and not isinstance(is_open, bool):
            return None
        fuel_prices = raw.get("fuel_prices")
        if fuel_prices is not None and not isinstance(fuel_prices, dict):
            return None
        fuel_fallbacks = raw.get("fuel_fallbacks")
        if fuel_fallbacks is not None and not isinstance(fuel_fallbacks, dict):
            return None
        return Station(
            station_id=raw["station_id"], name=raw["name"], brand=raw["brand"],
            price=number("price"), distance=number("distance"), is_open=is_open,
            street=raw["street"], house_number=raw["house_number"],
            postcode=raw["postcode"], place=raw["place"], latitude=latitude,
            longitude=longitude, currency=raw.get("currency"),
            price_updated_at=timestamp("price_updated_at"),
            country_code=raw.get("country_code"), provider=raw.get("provider"),
            price_confirmed_at=timestamp("price_confirmed_at"),
            price_age_hours=number("price_age_hours"),
            price_stale=raw.get("price_stale"), fuel_type=raw.get("fuel_type"),
            requested_fuel=raw.get("requested_fuel"),
            fallback_used=bool(raw.get("fallback_used", False)),
            fuel_prices=fuel_prices, fuel_fallbacks=fuel_fallbacks,
        )

    def _set_station_data(self, stations: list[Station]) -> None:
        """Update all derived station fields from a validated station list."""

        self.stations = stations
        self.nearest_station = nearest_station(stations)
        self.cheapest_stations = cheapest_by_fuel(stations)
        self.cheapest_station = self.cheapest_stations.get(
            self.fuel_types[0] if self.fuel_types else DEFAULT_SORT_FUEL
        )

    def _cancel_provider_cooldown_timer(self) -> None:
        cancel = getattr(self, "_cooldown_timer_unsub", None)
        self._cooldown_timer_unsub = None
        if cancel:
            cancel()

    def _schedule_provider_cooldown_refresh(self) -> None:
        if self.last_request is None:
            return
        remaining = self._provider_minimum_interval(
            self.options.get(CONF_PROVIDER_MODE)
        ) - (datetime.now().astimezone() - self.last_request)
        if remaining.total_seconds() <= 0:
            return
        if getattr(self, "_cooldown_timer_unsub", None) is not None:
            return

        @callback
        def _run(_now: datetime) -> None:
            self._cooldown_timer_unsub = None
            task = getattr(self, "_cooldown_refresh_task", None)
            if task is None or task.done():
                self._cooldown_refresh_task = self.hass.async_create_task(
                    self._async_cooldown_refresh()
                )

        self._cooldown_timer_unsub = async_call_later(
            self.hass, remaining.total_seconds(), _run
        )

    async def _async_cooldown_refresh(self) -> None:
        try:
            await self.async_request_refresh()
        except asyncio.CancelledError:
            raise
        finally:
            self._cooldown_refresh_task = None

    async def _set_provider_status(self, provider: str, status: str) -> None:
        """Persist only non-sensitive result state from a real provider call."""

        if not hasattr(self, "_provider_status_store") or not hasattr(self.hass, "data"):
            return
        domain_data = self.hass.data.setdefault(DOMAIN, {})
        all_status = domain_data.setdefault("provider_status", {}).setdefault(self.entry.entry_id, {})
        status_record = {
            "status": status,
            "checked_at": datetime.now().astimezone().isoformat(),
        }
        all_status[provider] = status_record
        self.provider_status = all_status
        await self._provider_status_store.async_save(all_status)

    async def async_shutdown(self) -> None:
        if self._unsub_position:
            self._unsub_position()
            self._unsub_position = None
        unsub_position_report = getattr(self, "_unsub_position_report", None)
        if unsub_position_report:
            unsub_position_report()
        self._unsub_position_report = None
        self.gps_listener_registered = False
        self._cancel_recovery_timer()
        self._cancel_provider_cooldown_timer()
        self._recovery_active = False
        cooldown_task = getattr(self, "_cooldown_refresh_task", None)
        self._cooldown_refresh_task = None
        if cooldown_task and not cooldown_task.done():
            cooldown_task.cancel()
        task = getattr(self, "_movement_refresh_task", None)
        self._movement_refresh_task = None
        if task and not task.done():
            task.cancel()
            self.recovery_task_status = "cancelled"
        recovery_task = getattr(self, "_recovery_task", None)
        self._recovery_task = None
        self._recovery_request_scheduled = False
        if recovery_task and not recovery_task.done() and recovery_task is not task:
            recovery_task.cancel()
        await super().async_shutdown()

    @property
    def adaptive_updates_enabled(self) -> bool:
        """Whether the opt-in adaptive schedule is active."""

        return bool(self.options.get(CONF_ADAPTIVE_UPDATES, False))

    @staticmethod
    def _adaptive_interval(speed_kmh: float | None) -> timedelta:
        if speed_kmh is None or speed_kmh <= 0:
            return ADAPTIVE_STATIONARY_INTERVAL
        if speed_kmh <= 30:
            return ADAPTIVE_CITY_INTERVAL
        if speed_kmh <= 70:
            return ADAPTIVE_COUNTRY_ROAD_INTERVAL
        return ADAPTIVE_MOTORWAY_INTERVAL

    def _provider_minimum_interval(self, provider: str | None) -> timedelta:
        if provider == "auto":
            # Auto mode may select Tankerkönig after a country transition;
            # never use a provider switch to bypass its five-minute floor.
            return _MIN_PROVIDER_INTERVALS[PROVIDER_TANKERKOENIG]
        return _MIN_PROVIDER_INTERVALS.get(provider or "", timedelta(0))

    def _set_adaptive_interval(self, speed_kmh: float | None) -> None:
        """Set Core's next regular interval, preserving the legacy mode."""

        if not self.adaptive_updates_enabled:
            return
        interval = self._adaptive_interval(speed_kmh)
        if interval < self._provider_minimum_interval(self.options.get(CONF_PROVIDER_MODE)):
            interval = self._provider_minimum_interval(self.options.get(CONF_PROVIDER_MODE))
        if getattr(self, "update_interval", None) == interval:
            return
        self.update_interval = interval
        # Core owns the periodic callback.  Reschedule it only when the
        # callback is currently installed; never create a second timer.
        unschedule = getattr(self, "_unschedule_refresh", None)
        schedule = getattr(self, "_schedule_refresh", None)
        if callable(unschedule) and callable(schedule) and getattr(self, "_unsub_refresh", None):
            unschedule()
            schedule()

    def async_schedule_startup_recovery(self) -> None:
        """Start bounded startup recovery after an initial GPS miss."""

        if self.recovery_status != "awaiting_location" and self.last_update_result != "provider_transient_failure":
            return
        if not self._recovery_active:
            self._recovery_active = True
            if self._recovery_started_at is None:
                self._recovery_started_at = datetime.now().astimezone()
            self._recovery_startup_index = 0
            self._recovery_transient_failures = 0
        self._request_recovery_refresh("startup_recheck")

    def _cancel_recovery_timer(self) -> None:
        cancel = getattr(self, "_recovery_timer_unsub", None)
        self._recovery_timer_unsub = None
        self.recovery_next_retry_at = None
        if cancel:
            cancel()

    def _schedule_recovery_timer(self, delay: float, trigger: str) -> None:
        if not self._recovery_active:
            return
        self._cancel_recovery_timer()
        self.recovery_trigger = trigger
        due = datetime.now().astimezone() + timedelta(seconds=delay)
        self.recovery_next_retry_at = due

        @callback
        def _run(_now: datetime) -> None:
            self._recovery_timer_unsub = None
            self.recovery_next_retry_at = None
            self._request_recovery_refresh("recovery_timer")

        self._recovery_timer_unsub = async_call_later(self.hass, delay, _run)

    def _schedule_next_startup_recovery(self) -> None:
        if self._recovery_startup_index < len(_STARTUP_RECOVERY_DELAYS):
            target_seconds = _STARTUP_RECOVERY_DELAYS[self._recovery_startup_index]
            self._recovery_startup_index += 1
            started_at = self._recovery_started_at or datetime.now().astimezone()
            elapsed = (datetime.now().astimezone() - started_at).total_seconds()
            delay = max(0.0, target_seconds - elapsed)
        else:
            delay = _STARTUP_RECOVERY_SLOW_INTERVAL
        self._schedule_recovery_timer(delay, "startup_retry")

    def _schedule_transient_recovery(self) -> None:
        self._recovery_transient_failures += 1
        delay = min(
            _RECOVERY_BACKOFF_CAP,
            _RECOVERY_BACKOFF_BASE * (2 ** (self._recovery_transient_failures - 1)),
        )
        delay = min(_RECOVERY_BACKOFF_CAP, delay + random.uniform(0, delay * 0.25))
        retry_after = self.last_retry_after
        if retry_after is not None:
            delay = max(delay, float(retry_after))
        self._schedule_recovery_timer(delay, "provider_transient_failure")

    def _finish_recovery(self) -> None:
        self._recovery_active = False
        self._cancel_recovery_timer()
        self.recovery_next_retry_at = None

    def _request_recovery_refresh(self, trigger: str) -> None:
        """Deduplicate GPS, timer, and startup recovery triggers."""

        if not self._recovery_active:
            return
        self.recovery_trigger = trigger
        if _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY]) is None:
            self.recovery_task_status = "waiting_for_gps"
            if self._recovery_timer_unsub is None:
                self._schedule_next_startup_recovery()
            return
        retry_not_before = self._retry_not_before
        now = datetime.now().astimezone()
        if retry_not_before and now < retry_not_before:
            if self._recovery_timer_unsub is None:
                self._schedule_recovery_timer(
                    (retry_not_before - now).total_seconds(), "retry_after"
                )
            return
        self._cancel_recovery_timer()
        task = getattr(self, "_recovery_task", None)
        if self._recovery_request_scheduled or (task and not task.done()):
            return
        self.recovery_attempt_count += 1
        self.recovery_task_status = "scheduled"
        self._recovery_request_scheduled = True
        self._recovery_task = self.hass.async_create_task(
            self._async_request_recovery_refresh()
        )

    async def _async_request_recovery_refresh(self) -> None:
        self.recovery_task_status = "running"
        try:
            await self.async_request_refresh()
        except asyncio.CancelledError:
            self.recovery_task_status = "cancelled"
            raise
        except Exception as err:
            self.recovery_error_class = type(err).__name__
            self.recovery_task_status = "failed"
            self._finish_recovery()
            raise
        finally:
            self._recovery_task = None
            self._recovery_request_scheduled = False
        result = self.last_update_result
        if result == "provider_success":
            self.recovery_error_class = None
            self.recovery_task_status = "completed"
            self._finish_recovery()
        elif result == "provider_transient_failure":
            self.recovery_error_class = self.last_update_error_class
            self.recovery_task_status = "retry_scheduled"
            self._schedule_transient_recovery()
        elif result == "gps_unavailable":
            self.recovery_task_status = "waiting_for_gps"
            self._schedule_next_startup_recovery()
        else:
            self.recovery_error_class = self.last_update_error_class
            self.recovery_task_status = "permanent_failure"
            self._finish_recovery()

    def _schedule_movement_refresh(self) -> None:
        """Schedule at most one movement/startup refresh task."""

        task = self._movement_refresh_task
        if self._movement_refresh_scheduled or (task and not task.done()):
            return
        self._movement_refresh_scheduled = True
        self.recovery_task_status = "scheduled"
        self._movement_refresh_task = self.hass.async_create_task(
            self._async_request_movement_refresh()
        )

    @staticmethod
    def _parse_time(value: Any) -> datetime | None:
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    async def _async_update_data(self) -> list[Station]:
        now = datetime.now().astimezone()
        self.last_update_attempt = now
        self.last_update_result = "started"
        if self._retry_not_before and now < self._retry_not_before:
            if _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY]):
                _LOGGER.debug(
                    "Skipping provider refresh during Retry-After window: provider=%s",
                    self.last_update_error_provider or "unknown",
                )
                self.last_update_result = "provider_transient_failure"
                return self.stations if self.stations else None

        configured_fuels = getattr(self, "fuel_types", self._configured_fuels(self.options))
        position = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        if position is None:
            if self._is_auto:
                decision = AutoProviderDecision(
                    None, None, CountryPriceCoverage.UNKNOWN, "location_unavailable"
                )
                self._set_auto_runtime_state(decision)
            if self.stations:
                self.data_stale = True
                self.recovery_status = "awaiting_location"
                return self.stations
            # A tracker can be unknown during HA startup.  Return an empty
            # successful result so entities are created and the state-change
            # listener can trigger the first real refresh when GPS appears.
            self.recovery_status = "awaiting_location"
            self.data_stale = False
            self.last_update_result = "gps_unavailable"
            # None means that no provider search has produced a result yet.
            # An empty list is reserved for a successful search with zero
            # stations, so the overview entity can distinguish unavailable
            # startup data from a real zero-result response.
            return None
        gps_sample = self._current_gps_sample(position)
        if self.adaptive_updates_enabled and gps_sample is None:
            if self.stations:
                self.data_stale = True
                self.recovery_status = "awaiting_location"
                return self.stations
            self.recovery_status = "awaiting_location"
            self.last_update_result = "gps_unavailable"
            return None
        if gps_sample is not None:
            self.last_gps_sample = gps_sample
            self._set_adaptive_interval(gps_sample.speed_kmh)
        observed_decision = self.country_auto_context.observe_position(position)
        if self._is_auto:
            decision = observed_decision
            self._set_auto_runtime_state(decision)
            requests = []
            for index, requested_fuel in enumerate(configured_fuels):
                candidate = decision if index == 0 else choose_auto_provider(
                    self.country_auto_context.confirmed_country,
                    requested_fuel,
                    tankerkoenig_enabled=PROVIDER_REGISTRY[PROVIDER_TANKERKOENIG].enabled and PROVIDER_TANKERKOENIG in self.available_provider_modes,
                    tankerkoenig_capabilities=PROVIDER_REGISTRY[PROVIDER_TANKERKOENIG].capabilities,
                    petromap_enabled=PROVIDER_REGISTRY[PROVIDER_PETROMAP].enabled and PROVIDER_PETROMAP in self.available_provider_modes,
                    petromap_capabilities=PROVIDER_REGISTRY[PROVIDER_PETROMAP].capabilities,
                    nakordoni_enabled=PROVIDER_REGISTRY[PROVIDER_NAKORDONI].enabled and PROVIDER_NAKORDONI in self.available_provider_modes,
                    nakordoni_capabilities=PROVIDER_REGISTRY[PROVIDER_NAKORDONI].capabilities,
                )
                try:
                    validate_direct_fuel_runtime(candidate)
                except (NoSuitableProviderError, FuelFallbackBlockedError):
                    continue
                effective_fuel = candidate.fuel_resolution.effective_fuel if candidate.fuel_resolution else None
                if effective_fuel is None or candidate.provider_mode is None:
                    continue
                requests.append((candidate.provider_mode, self._get_provider(candidate.provider_mode), requested_fuel, effective_fuel))
            if not requests:
                raise UpdateFailed("No configured fuel has a suitable provider") from NoSuitableProviderError(
                    decision.reason
                )
            provider_mode = requests[0][0]
            provider = requests[0][1]
        else:
            provider_mode = self.options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            available_provider_modes = getattr(self, "available_provider_modes", frozenset({provider_mode}))
            if provider_mode not in available_provider_modes or self.client is None:
                raise UpdateFailed("Selected provider has no configured API key")
            provider = self.client
            capabilities = PROVIDER_REGISTRY[provider_mode].capabilities
            requests = []
            for requested_fuel in configured_fuels:
                resolution = resolve_fuel(requested_fuel, capabilities)
                if resolution.effective_fuel is not None:
                    requests.append((provider_mode, provider, requested_fuel, resolution.effective_fuel))
            if not requests:
                raise UpdateFailed(
                    str(ProviderUnsupportedFuelError(
                        f"{provider_mode} does not support configured fuels"
                    ))
                )
        provider_minimum = self._provider_minimum_interval(provider_mode)
        if (
            self.last_request is not None
            and now - self.last_request < provider_minimum
        ):
            self.last_update_result = "provider_cooldown"
            self.data_stale = bool(self.stations)
            self._schedule_provider_cooldown_refresh()
            return self.stations if self.stations else None
        provider_lock = getattr(self, "_provider_lock", None)
        if provider_lock is None:
            provider_lock = asyncio.Lock()
            self._provider_lock = provider_lock
        if getattr(self, "recovery_provider_in_flight", False):
            self.last_update_result = "provider_in_flight"
            return self.stations if self.stations else None
        await provider_lock.acquire()
        if getattr(self, "recovery_provider_in_flight", False):
            provider_lock.release()
            self.last_update_result = "provider_in_flight"
            return self.stations if self.stations else None
        self.last_request = now
        self.last_provider_attempt = now
        if self._is_auto:
            self._set_auto_runtime_state(decision, effective_provider=provider_mode)
        result: list[Station] = []
        active_provider_mode = provider_mode
        self.recovery_provider_in_flight = True
        try:
            for request_mode, request_provider, requested_fuel, effective_fuel in requests:
                active_provider_mode = request_mode
                found = await request_provider.async_search(
                    StationSearchQuery(
                        latitude=position[0],
                        longitude=position[1],
                        radius_km=min(float(self.options[CONF_RADIUS]), MAX_API_RADIUS_KM),
                        fuel_type=effective_fuel,
                        station_count=int(self.options[CONF_STATION_COUNT]),
                    )
                )
                self.last_provider_success = datetime.now().astimezone()
                await self._set_provider_status(request_mode, "success")
                if len(requests) > 1 or requested_fuel != effective_fuel:
                    found = [replace(
                        station,
                        station_id=station.station_id,
                        fuel_type=effective_fuel,
                        requested_fuel=requested_fuel,
                        fallback_used=requested_fuel != effective_fuel,
                        provider=station.provider or request_mode,
                    ) for station in found]
                result.extend(found)
        except ProviderAuthError as err:
            self.last_update_result = "provider_auth_failed"
            if getattr(self, "_recovery_active", False):
                self._finish_recovery()
            await self._set_provider_status(active_provider_mode, "auth_failed")
            if active_provider_mode == PROVIDER_NAKORDONI:
                self._record_nakordoni_failure(err)
            if active_provider_mode in (PROVIDER_PETROMAP, PROVIDER_NAKORDONI):
                self.entry.async_start_reauth(
                    self.hass,
                    context=ProviderReauthContext(active_provider_mode).as_dict(),
                )
                raise ConfigEntryAuthFailed("API authentication failed") from err
            raise UpdateFailed("API authentication failed") from err
        except ProviderRateLimitError as err:
            self.last_update_result = "provider_rate_limited"
            await self._set_provider_status(active_provider_mode, "uncheckable")
            if active_provider_mode == PROVIDER_NAKORDONI:
                self._record_nakordoni_failure(err)
            return await self._handle_transient_failure(
                err, active_provider_mode, position,
                self._nakordoni_error_message(err)
                if active_provider_mode == PROVIDER_NAKORDONI
                else "API rate limit reached",
            )
        except ProviderError as err:
            self.last_update_result = "provider_failed"
            diagnostics = getattr(err, "diagnostics", None)
            status = "approval_pending" if getattr(diagnostics, "error_code", None) == "not_approved" else "uncheckable"
            if isinstance(err, ProviderAuthError):
                status = "auth_failed"
            await self._set_provider_status(active_provider_mode, status)
            if active_provider_mode == PROVIDER_NAKORDONI:
                self._record_nakordoni_failure(err)
                message = self._nakordoni_error_message(err)
            else:
                provider_label = active_provider_mode or "provider"
                message = f"{provider_label} request failed"
            if isinstance(err, _TRANSIENT_PROVIDER_ERRORS):
                return await self._handle_transient_failure(
                    err, active_provider_mode, position, message,
                )
            if getattr(self, "_recovery_active", False):
                self._finish_recovery()
            raise UpdateFailed(message) from err
        finally:
            self.recovery_provider_in_flight = False
            provider_lock.release()
        result = merge_stations(result)
        self._cancel_provider_cooldown_timer()
        self._set_station_data(result)
        if provider_mode == PROVIDER_NAKORDONI:
            self._record_nakordoni_success(provider)
        sorted_stations = sort_stations(
            result,
            int(self.options[CONF_STATION_COUNT]),
            mode=self.options.get(CONF_SORT_MODE, DEFAULT_SORT_MODE),
            fuel=self.options.get(
                CONF_SORT_FUEL,
                getattr(self, "fuel_types", configured_fuels)[0] if configured_fuels else DEFAULT_SORT_FUEL,
            ),
        )
        self.stations = sorted_stations
        self.last_successful_update = now
        self.reference_position = position
        recovered = self.data_stale
        self.data_stale = False
        self.last_update_error_at = None
        self.last_update_error_class = None
        self.last_update_error_provider = None
        self.last_retry_after = None
        self._retry_not_before = None
        self.consecutive_failures = 0
        self.recovery_status = "recovered" if recovered else "success"
        self.last_update_result = "provider_success"
        if getattr(self, "_recovery_active", False):
            self._finish_recovery()
        await self._store.async_save({
            "last_successful_update": now.isoformat(),
            "last_request": now.isoformat(),
            "last_update_attempt": now.isoformat(),
            "last_update_error_at": None,
            "last_update_error_class": None,
            "last_update_error_provider": None,
            "last_retry_after": None,
            "data_stale": False,
            "recovery_status": self.recovery_status,
            "consecutive_failures": 0,
            "reference_latitude": position[0],
            "reference_longitude": position[1],
            "last_gps_latitude": self.last_gps_sample.position[0]
            if self.last_gps_sample else None,
            "last_gps_longitude": self.last_gps_sample.position[1]
            if self.last_gps_sample else None,
            "last_gps_at": self.last_gps_sample.observed_at.isoformat()
            if self.last_gps_sample else None,
            _CACHE_CONTEXT_KEY: self._cache_context(),
            _STATION_CACHE_KEY: [self._station_to_store(station) for station in self.stations],
        })
        return self.stations

    async def _handle_transient_failure(
        self,
        error: ProviderError,
        provider: str,
        position: tuple[float, float] | None,
        message: str,
    ) -> list[Station]:
        """Keep valid data visible while allowing the next scheduled poll to recover."""

        now = datetime.now().astimezone()
        retry_after = _retry_after_seconds(error)
        self.last_update_error_at = now
        self.last_update_error_class = type(error).__name__
        self.last_update_error_provider = provider
        self.last_update_result = "provider_transient_failure"
        self.last_retry_after = retry_after
        self.consecutive_failures += 1
        self.recovery_status = "retry_scheduled" if self.stations and position else "failed"
        self.data_stale = bool(self.stations and position)
        self._retry_not_before = (
            now + timedelta(seconds=retry_after) if retry_after is not None else None
        )
        _LOGGER.warning(
            "Mobile Fuel Stations refresh failed: provider=%s error_class=%s "
            "cached_data=%s retry_after=%s consecutive_failures=%s",
            provider,
            type(error).__name__,
            self.data_stale,
            retry_after,
            self.consecutive_failures,
        )
        await self._store.async_save({
            "last_successful_update": self.last_successful_update.isoformat()
            if self.last_successful_update else None,
            "last_request": self.last_request.isoformat() if self.last_request else None,
            "last_update_attempt": self.last_update_attempt.isoformat()
            if self.last_update_attempt else None,
            "last_update_error_at": now.isoformat(),
            "last_update_error_class": type(error).__name__,
            "last_update_error_provider": provider,
            "last_retry_after": retry_after,
            "data_stale": self.data_stale,
            "recovery_status": self.recovery_status,
            "consecutive_failures": self.consecutive_failures,
            "reference_latitude": position[0] if position else None,
            "reference_longitude": position[1] if position else None,
            _CACHE_CONTEXT_KEY: self._cache_context(),
            _STATION_CACHE_KEY: [self._station_to_store(station) for station in self.stations],
        })
        if self.data_stale:
            return self.stations
        # A transient provider failure before the first successful result must
        # not abort config-entry setup.  The coordinator remains available
        # with an empty result and the regular poll will retry automatically.
        return None

    def _current_gps_sample(
        self, position: tuple[float, float] | None = None
    ) -> GpsSample | None:
        sample = _gps_sample(
            self.hass,
            self.options[CONF_LOCATION_ENTITY],
            previous=getattr(self, "last_gps_sample", None),
        )
        if sample is not None:
            return sample
        # Keep the legacy test and compatibility path for HA states that do
        # not expose timestamps or for startup fixtures with only coordinates.
        if getattr(self.hass, "states", None) is not None:
            return None
        if position is None:
            position = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        if position is None:
            return None
        return GpsSample(position, datetime.now().astimezone(), None, None)

    def _process_gps_event(self, event: Event, event_type: str) -> None:
        """Process state and attribute-only reports through one deduplicated path."""

        self._record_gps_event(event, event_type)
        sample = self._current_gps_sample()
        if sample is None:
            return
        self.last_gps_sample = sample
        event_key = (*sample.position, sample.observed_at)
        if event_key == getattr(self, "_last_gps_event_key", None):
            return
        self._last_gps_event_key = event_key
        self._set_adaptive_interval(sample.speed_kmh)

        if self._recovery_active:
            self._request_recovery_refresh(f"gps_{event_type}")
            return
        if not self.options.get(CONF_MOVEMENT_UPDATES, True):
            return
        # During HA startup the tracker may become valid after the initial
        # coordinator refresh.  There is no movement baseline yet, so the
        # first valid position itself is the refresh trigger.
        if self.reference_position is None or self.last_request is None:
            self._schedule_movement_refresh()
            return
        now = datetime.now().astimezone()
        if self._retry_not_before and now < self._retry_not_before:
            return
        elapsed = now - self.last_request
        threshold = (
            DEFAULT_ADAPTIVE_MOVEMENT_THRESHOLD_KM
            if self.adaptive_updates_enabled
            else float(self.options[CONF_MOVEMENT_THRESHOLD])
        )
        distance = haversine_km(self.reference_position, sample.position)
        if distance < threshold:
            return
        cooldown = timedelta(minutes=float(self.options[CONF_COOLDOWN]))
        provider_mode = self.options.get(CONF_PROVIDER_MODE)
        if self.adaptive_updates_enabled and provider_mode == "auto":
            provider_minimum = self._provider_minimum_interval(PROVIDER_TANKERKOENIG)
        else:
            provider_minimum = self._provider_minimum_interval(provider_mode)
        if elapsed < max(cooldown, provider_minimum):
            return
        self._schedule_movement_refresh()

    @callback
    def _async_position_changed(self, event: Event) -> None:
        self._process_gps_event(event, "state_changed")

    @callback
    def _async_position_reported(self, event: Event) -> None:
        """Handle GPS attribute-only updates through the same movement path."""

        self._process_gps_event(event, "state_reported")

    def _record_gps_event(self, event: Event, event_type: str) -> None:
        self.recovery_last_gps_event_type = event_type
        self.recovery_last_gps_event_at = datetime.now().astimezone()

    async def _async_request_movement_refresh(self) -> None:
        self.recovery_task_status = "running"
        try:
            await self.async_request_refresh()
        except asyncio.CancelledError:
            self.recovery_task_status = "cancelled"
            raise
        except Exception:
            self.recovery_task_status = "failed"
            raise
        else:
            self.recovery_task_status = "completed"
        finally:
            self._movement_refresh_scheduled = False
            self._movement_refresh_task = None

    @property
    def current_distance_km(self) -> float | None:
        if self.reference_position is None:
            return None
        current = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        return haversine_km(self.reference_position, current) if current else None

    @property
    def gps_available(self) -> bool:
        """Expose only whether the configured tracker currently has a position."""

        return _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY]) is not None

    @property
    def data_age_seconds(self) -> float | None:
        """Return the age of the last successful provider result."""

        if self.last_successful_update is None:
            return None
        return max(0.0, (datetime.now().astimezone() - self.last_successful_update).total_seconds())

    @property
    def config(self) -> dict[str, Any]:
        return self.options
