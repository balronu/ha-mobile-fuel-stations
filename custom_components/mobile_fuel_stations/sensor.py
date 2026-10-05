"""Sensors for Mobile Fuel Stations."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Station
from .const import CONF_STATION_COUNT, DOMAIN
from .coordinator import MobileFuelStationsCoordinator


type MobileFuelStationsEntry = ConfigEntry[MobileFuelStationsCoordinator]


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Tankerkönig",
        model="Mobile Fuel Stations",
    )


async def async_setup_entry(hass, entry: MobileFuelStationsEntry, async_add_entities) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [OverviewSensor(coordinator, entry)]
    entities.extend(
        StationSlotSensor(coordinator, entry, index)
        for index in range(int(coordinator.config[CONF_STATION_COUNT]))
    )
    async_add_entities(entities)


class OverviewSensor(CoordinatorEntity[MobileFuelStationsCoordinator], SensorEntity):
    """Number of current nearby stations."""

    _attr_icon = "mdi:gas-station"
    _attr_name = "Nearby Stations"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_nearby_stations"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self):
        ref = self.coordinator.reference_position
        return {
            "radius": self.coordinator.config["radius"],
            "fuel_type": self.coordinator.config["fuel_type"],
            "location_entity": self.coordinator.config["location_entity"],
            "station_count": self.coordinator.config["station_count"],
            "last_successful_update": self.coordinator.last_successful_update.isoformat()
            if self.coordinator.last_successful_update
            else None,
            "reference_latitude": ref[0] if ref else None,
            "reference_longitude": ref[1] if ref else None,
            "distance_since_last_search": self.coordinator.current_distance_km,
        }


class StationSlotSensor(CoordinatorEntity[MobileFuelStationsCoordinator], SensorEntity):
    """A stable slot containing the station currently assigned to it."""

    _attr_native_unit_of_measurement = "EUR/L"
    _attr_suggested_display_precision = 3

    def __init__(self, coordinator, entry, index: int) -> None:
        super().__init__(coordinator)
        self.index = index
        self._attr_unique_id = f"{entry.entry_id}_station_slot_{index + 1}"
        self._attr_name = f"Station {index + 1}"
        self._attr_device_info = _device_info(entry)

    @property
    def station(self) -> Station | None:
        data = self.coordinator.data or []
        return data[self.index] if self.index < len(data) else None

    @property
    def native_value(self) -> float | None:
        return self.station.price if self.station else None

    @property
    def available(self) -> bool:
        return self.station is not None and super().available

    @property
    def icon(self) -> str:
        return "mdi:gas-station" if self.station and self.station.is_open else "mdi:gas-station-off"

    @property
    def extra_state_attributes(self):
        station = self.station
        if station is None:
            return {"station_id": None}
        return {
            "station_id": station.station_id,
            "station_name": station.name,
            "brand": station.brand,
            "distance": station.distance,
            "is_open": station.is_open,
            "street": station.street,
            "house_number": station.house_number,
            "postcode": station.postcode,
            "place": station.place,
            "latitude": station.latitude,
            "longitude": station.longitude,
        }
