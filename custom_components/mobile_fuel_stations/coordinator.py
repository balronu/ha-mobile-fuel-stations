"""Coordinator with persistent successful-search state and movement refreshes."""

from __future__ import annotations

from datetime import datetime, timedelta
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

from .api import Station, cheapest_station, nearest_station, sort_stations
from .const import (
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_UPDATE_INTERVAL,
    CONF_PROVIDER_MODE,
    DOMAIN,
    MAX_API_RADIUS_KM,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
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
    ProviderReauthContext,
    ProviderUnsupportedFuelError,
    StationSearchQuery,
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
        self.auto_provider_decision = choose_auto_provider(
            self.confirmed_country,
            self.fuel_type,
            tankerkoenig_enabled=tankerkoenig.enabled,
            tankerkoenig_capabilities=tankerkoenig.capabilities,
            petromap_enabled=petromap.enabled,
            petromap_capabilities=petromap.capabilities,
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
        self.last_successful_update: datetime | None = None
        self.reference_position: tuple[float, float] | None = None
        self.last_request: datetime | None = None
        self._unsub_position = None
        self._movement_refresh_scheduled = False
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry.entry_id}")
        self.country_auto_context = CountryAutoContext(self.options[CONF_FUEL_TYPE])
        self.auto_runtime_state: AutoRuntimeState | None = None

    @property
    def _is_auto(self) -> bool:
        return self.options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG) == "auto"

    def _get_provider(self, provider_mode: str):
        """Return one cached concrete provider for Auto runtime."""

        if provider_mode not in (PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP):
            raise ValueError(f"Auto selected non-concrete provider: {provider_mode}")
        provider = self._providers.get(provider_mode)
        if provider is not None:
            return provider
        registration = PROVIDER_REGISTRY[provider_mode]
        key_name = (
            "tankerkoenig_api_key"
            if provider_mode == PROVIDER_TANKERKOENIG
            else "petromap_api_key"
        )
        provider = registration.factory(self._session, self.options[key_name])
        self._providers[provider_mode] = provider
        return provider

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
            try:
                validate_direct_fuel_runtime(decision)
            except (NoSuitableProviderError, FuelFallbackBlockedError) as err:
                raise UpdateFailed(str(err)) from err
            provider_mode = decision.provider_mode
            provider = self._get_provider(provider_mode)
            query_fuel = decision.fuel_resolution.effective_fuel
        else:
            provider_mode = self.options.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            provider = self.client
            query_fuel = self.options[CONF_FUEL_TYPE]
            capabilities = PROVIDER_REGISTRY[provider_mode].capabilities
            if query_fuel not in (capabilities.supported_fuel_types or frozenset()):
                raise UpdateFailed(
                    str(ProviderUnsupportedFuelError(
                        f"{provider_mode} does not support fuel {query_fuel}"
                    ))
                )
        now = datetime.now().astimezone()
        self.last_request = now
        if self._is_auto:
            self._set_auto_runtime_state(decision, effective_provider=provider_mode)
        try:
            result = await provider.async_search(
                StationSearchQuery(
                    latitude=position[0],
                    longitude=position[1],
                    radius_km=min(float(self.options[CONF_RADIUS]), MAX_API_RADIUS_KM),
                    fuel_type=query_fuel,
                )
            )
        except ProviderAuthError as err:
            if provider_mode == PROVIDER_PETROMAP:
                if self._is_auto:
                    self.entry.async_start_reauth(
                        self.hass,
                        context=ProviderReauthContext(PROVIDER_PETROMAP).as_dict(),
                    )
                raise ConfigEntryAuthFailed("API authentication failed") from err
            raise UpdateFailed("API authentication failed") from err
        except ProviderRateLimitError as err:
            raise UpdateFailed("API rate limit reached") from err
        except ProviderError as err:
            provider_label = provider_mode or "provider"
            raise UpdateFailed(f"{provider_label} request failed") from err
        self.nearest_station = nearest_station(result)
        self.cheapest_station = cheapest_station(result)
        self.stations = sort_stations(result, int(self.options[CONF_STATION_COUNT]))
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
