"""Coordinator with persistent successful-search state and movement refreshes."""

from __future__ import annotations

from datetime import datetime, timedelta
from dataclasses import replace
import json
import logging
from math import asin, cos, radians, sin, sqrt
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry, ConfigEntryAuthFailed
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import Station, cheapest_by_fuel, nearest_station, sort_stations, merge_stations
from .const import (
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_FUEL_TYPES,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_UPDATE_INTERVAL,
    CONF_PROVIDER_MODE,
    CONF_SORT_FUEL,
    CONF_SORT_MODE,
    DEFAULT_SORT_FUEL,
    DEFAULT_SORT_MODE,
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
    ProviderRateLimitError,
    ProviderRequestDiagnostics,
    ProviderReauthContext,
    ProviderUnsupportedFuelError,
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
    ) -> None:
        self.fuel_type = fuel_type
        self._resolver = resolver
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
            tankerkoenig_enabled=tankerkoenig.enabled,
            tankerkoenig_capabilities=tankerkoenig.capabilities,
            petromap_enabled=petromap.enabled,
            petromap_capabilities=petromap.capabilities,
            nakordoni_enabled=nakordoni.enabled,
            nakordoni_capabilities=nakordoni.capabilities,
        )
        return self.auto_provider_decision


class MobileFuelStationsCoordinator(DataUpdateCoordinator[list[Station]]):
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
            self.client = create_provider(self._session, self.options)
        self.stations: list[Station] = []
        self.nearest_station: Station | None = None
        self.cheapest_station: Station | None = None
        self.cheapest_stations: dict[str, Station] = {}
        self.last_successful_update: datetime | None = None
        self.reference_position: tuple[float, float] | None = None
        self.last_request: datetime | None = None
        self._unsub_position = None
        self._movement_refresh_scheduled = False
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry.entry_id}")
        self.fuel_types = self._configured_fuels(self.options)
        self.country_auto_context = CountryAutoContext(self.fuel_types[0])
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
            lat, lon = stored.get("reference_latitude"), stored.get("reference_longitude")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                self.reference_position = (float(lat), float(lon))
        if self.options.get(CONF_MOVEMENT_UPDATES, True):
            self._unsub_position = async_track_state_change_event(
                self.hass, [self.options[CONF_LOCATION_ENTITY]], self._async_position_changed
            )

    async def async_shutdown(self) -> None:
        if self._unsub_position:
            self._unsub_position()

    @staticmethod
    def _parse_time(value: Any) -> datetime | None:
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    async def _async_update_data(self) -> list[Station]:
        configured_fuels = getattr(self, "fuel_types", self._configured_fuels(self.options))
        position = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        if position is None:
            if self._is_auto:
                decision = AutoProviderDecision(
                    None, None, CountryPriceCoverage.UNKNOWN, "location_unavailable"
                )
                self._set_auto_runtime_state(decision)
                raise UpdateFailed("Auto location is unavailable") from NoSuitableProviderError(
                    decision.reason
                )
            if self.stations:
                return self.stations
            raise UpdateFailed("Location entity has no valid GPS coordinates")
        observed_decision = self.country_auto_context.observe_position(position)
        if self._is_auto:
            decision = observed_decision
            self._set_auto_runtime_state(decision)
            requests = []
            for index, requested_fuel in enumerate(configured_fuels):
                candidate = decision if index == 0 else choose_auto_provider(
                    self.country_auto_context.confirmed_country,
                    requested_fuel,
                    tankerkoenig_enabled=PROVIDER_REGISTRY[PROVIDER_TANKERKOENIG].enabled,
                    tankerkoenig_capabilities=PROVIDER_REGISTRY[PROVIDER_TANKERKOENIG].capabilities,
                    petromap_enabled=PROVIDER_REGISTRY[PROVIDER_PETROMAP].enabled,
                    petromap_capabilities=PROVIDER_REGISTRY[PROVIDER_PETROMAP].capabilities,
                    nakordoni_enabled=PROVIDER_REGISTRY[PROVIDER_NAKORDONI].enabled,
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
        now = datetime.now().astimezone()
        self.last_request = now
        if self._is_auto:
            self._set_auto_runtime_state(decision, effective_provider=provider_mode)
        result: list[Station] = []
        try:
            for request_mode, request_provider, requested_fuel, effective_fuel in requests:
                found = await request_provider.async_search(
                    StationSearchQuery(
                        latitude=position[0],
                        longitude=position[1],
                        radius_km=min(float(self.options[CONF_RADIUS]), MAX_API_RADIUS_KM),
                        fuel_type=effective_fuel,
                        station_count=int(self.options[CONF_STATION_COUNT]),
                    )
                )
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
            if provider_mode == PROVIDER_NAKORDONI:
                self._record_nakordoni_failure(err)
            if provider_mode in (PROVIDER_PETROMAP, PROVIDER_NAKORDONI):
                self.entry.async_start_reauth(
                    self.hass,
                    context=ProviderReauthContext(provider_mode).as_dict(),
                )
                raise ConfigEntryAuthFailed("API authentication failed") from err
            raise UpdateFailed("API authentication failed") from err
        except ProviderRateLimitError as err:
            if provider_mode == PROVIDER_NAKORDONI:
                self._record_nakordoni_failure(err)
                raise UpdateFailed(self._nakordoni_error_message(err)) from err
            raise UpdateFailed("API rate limit reached") from err
        except ProviderError as err:
            if provider_mode == PROVIDER_NAKORDONI:
                self._record_nakordoni_failure(err)
                raise UpdateFailed(self._nakordoni_error_message(err)) from err
            provider_label = provider_mode or "provider"
            raise UpdateFailed(f"{provider_label} request failed") from err
        result = merge_stations(result)
        self.nearest_station = nearest_station(result)
        if provider_mode == PROVIDER_NAKORDONI:
            self._record_nakordoni_success(provider)
        self.cheapest_stations = cheapest_by_fuel(result)
        self.cheapest_station = self.cheapest_stations.get(self.fuel_types[0])
        self.stations = sort_stations(
            result,
            int(self.options[CONF_STATION_COUNT]),
            mode=self.options.get(CONF_SORT_MODE, DEFAULT_SORT_MODE),
            fuel=self.options.get(CONF_SORT_FUEL, self.fuel_types[0] if self.fuel_types else DEFAULT_SORT_FUEL),
        )
        self.last_successful_update = now
        self.reference_position = position
        await self._store.async_save({
            "last_successful_update": now.isoformat(),
            "last_request": now.isoformat(),
            "reference_latitude": position[0],
            "reference_longitude": position[1],
        })
        return self.stations

    @callback
    def _async_position_changed(self, event: Event) -> None:
        if self.reference_position is None or self.last_request is None:
            return
        current = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        if current is None:
            return
        elapsed = datetime.now().astimezone() - self.last_request
        distance = haversine_km(self.reference_position, current)
        if distance < float(self.options[CONF_MOVEMENT_THRESHOLD]):
            return
        if elapsed < timedelta(minutes=float(self.options[CONF_COOLDOWN])):
            return
        if not self._movement_refresh_scheduled:
            self._movement_refresh_scheduled = True
            self.hass.async_create_task(self._async_request_movement_refresh())

    async def _async_request_movement_refresh(self) -> None:
        try:
            await self.async_request_refresh()
        finally:
            self._movement_refresh_scheduled = False

    @property
    def current_distance_km(self) -> float | None:
        if self.reference_position is None:
            return None
        current = _valid_position(self.hass, self.options[CONF_LOCATION_ENTITY])
        return haversine_km(self.reference_position, current) if current else None

    @property
    def config(self) -> dict[str, Any]:
        return self.options
