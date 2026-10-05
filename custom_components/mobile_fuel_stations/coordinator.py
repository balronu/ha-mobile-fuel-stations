"""Coordinator with persistent successful-search state and movement refreshes."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from math import asin, cos, radians, sin, sqrt
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    MobileFuelStationsAuthError,
    MobileFuelStationsError,
    MobileFuelStationsRateLimitError,
    Station,
    TankerkoenigClient,
    cheapest_station,
    nearest_station,
    sort_stations,
)
from .const import (
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
    MAX_API_RADIUS_KM,
    STORAGE_KEY,
    STORAGE_VERSION,
)

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
        self.client = TankerkoenigClient(async_get_clientsession(hass), entry.data["api_key"])
        self.stations: list[Station] = []
        self.nearest_station: Station | None = None
        self.cheapest_station: Station | None = None
        self.last_successful_update: datetime | None = None
        self.reference_position: tuple[float, float] | None = None
        self.last_request: datetime | None = None
        self._unsub_position = None
        self._movement_refresh_scheduled = False
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry.entry_id}")

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
            if self.stations:
                return self.stations
            raise UpdateFailed("Location entity has no valid GPS coordinates")
        now = datetime.now().astimezone()
        self.last_request = now
        try:
            result = await self.client.async_search(
                position[0],
                position[1],
                min(float(self.options[CONF_RADIUS]), MAX_API_RADIUS_KM),
                self.options[CONF_FUEL_TYPE],
            )
        except MobileFuelStationsAuthError as err:
            raise UpdateFailed("API authentication failed") from err
        except MobileFuelStationsRateLimitError as err:
            raise UpdateFailed("API rate limit reached") from err
        except MobileFuelStationsError as err:
            raise UpdateFailed("Tankerkönig request failed") from err
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
