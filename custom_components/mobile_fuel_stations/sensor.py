"""Sensors for Mobile Fuel Stations."""

from __future__ import annotations

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Station, station_attributes
from .const import (
    CONF_PROVIDER_MODE,
    CONF_STATION_COUNT,
    DOMAIN,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
    PROVIDER_NAKORDONI,
)
from .coordinator import MobileFuelStationsCoordinator


type MobileFuelStationsEntry = ConfigEntry[MobileFuelStationsCoordinator]


def _registered_station_entity_ids(hass, entry: ConfigEntry, station_count: int) -> list[str]:
    """Return this entry's registered station-slot entity IDs in slot order.

    The station entity IDs are allocated by Home Assistant.  Resolve them from
    the entity registry using the slots' stable unique IDs instead of
    reconstructing entity IDs from a slug or an assumed naming convention.
    """

    registry = er.async_get(hass)
    entity_ids: list[str] = []
    for index in range(station_count):
        unique_id = f"{entry.entry_id}_station_slot_{index + 1}"
        entity_id = registry.async_get_entity_id(SENSOR_DOMAIN, DOMAIN, unique_id)
        if entity_id is not None:
            entity_ids.append(entity_id)
    return entity_ids


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    provider_mode = entry.options.get(
        CONF_PROVIDER_MODE,
        entry.data.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG),
    )
    manufacturer = {
        PROVIDER_TANKERKOENIG: "Tankerkönig",
        PROVIDER_PETROMAP: "Petromap",
        PROVIDER_AUTO: "Mobile Fuel Stations",
        PROVIDER_NAKORDONI: "Nakordoni",
    }.get(provider_mode, "Mobile Fuel Stations")
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer=manufacturer,
        model="Mobile Fuel Stations",
    )


async def async_setup_entry(hass, entry: MobileFuelStationsEntry, async_add_entities) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [OverviewSensor(coordinator, entry)]
    entities.extend(
        StationSlotSensor(coordinator, entry, index)
        for index in range(int(coordinator.config[CONF_STATION_COUNT]))
    )
    if coordinator.nakordoni_usage_enabled:
        entities.extend(
            (
                NakordoniCallsRemainingSensor(coordinator, entry),
                NakordoniQuotaResetSensor(coordinator, entry),
                NakordoniTripPassSensor(coordinator, entry),
            )
        )
    async_add_entities(entities)


class _NakordoniUsageSensor(CoordinatorEntity[MobileFuelStationsCoordinator], SensorEntity):
    """Base for account-usage entities; never exposes credential material."""

    def __init__(self, coordinator, entry, suffix: str, name: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_nakordoni_{suffix}"
        self._attr_name = name
        self._attr_device_info = _device_info(entry)

    @property
    def available(self) -> bool:
        return self.coordinator.nakordoni_account_usage is not None and super().available

    @property
    def extra_state_attributes(self):
        usage = self.coordinator.nakordoni_account_usage
        if usage is None:
            return {
                "last_attempt": self.coordinator.nakordoni_usage_last_attempt.isoformat()
                if self.coordinator.nakordoni_usage_last_attempt else None,
                "error": self.coordinator.nakordoni_usage_error,
                "upgrade_url": self.coordinator.nakordoni_usage_upgrade_url,
                "pass_url": self.coordinator.nakordoni_usage_pass_url,
                "reset_at": self.coordinator.nakordoni_usage_reset_at.isoformat()
                if self.coordinator.nakordoni_usage_reset_at else None,
            }
        attributes = usage.as_diagnostics()
        attributes.update({
            "last_success": self.coordinator.nakordoni_usage_last_success.isoformat()
            if self.coordinator.nakordoni_usage_last_success else None,
            "last_error": self.coordinator.nakordoni_usage_error,
            "last_error_at": self.coordinator.nakordoni_usage_error_at.isoformat()
            if self.coordinator.nakordoni_usage_error_at else None,
        })
        return attributes


class NakordoniCallsRemainingSensor(_NakordoniUsageSensor):
    """Cheap daily calls remaining, as documented by Nakordoni."""

    _attr_icon = "mdi:counter"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "calls_remaining", "Nakordoni calls remaining")

    @property
    def native_value(self) -> int | None:
        usage = self.coordinator.nakordoni_account_usage
        return usage.cheap.remaining if usage else None


class NakordoniQuotaResetSensor(_NakordoniUsageSensor):
    """Timestamp at which the cheap quota resets."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-refresh"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "quota_reset", "Nakordoni quota reset")

    @property
    def native_value(self):
        usage = self.coordinator.nakordoni_account_usage
        return usage.cheap.reset_at if usage else None


class NakordoniTripPassSensor(_NakordoniUsageSensor):
    """Trip Pass state and expiry metadata."""

    _attr_icon = "mdi:ticket-confirmation"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "trip_pass", "Nakordoni Trip Pass")

    @property
    def native_value(self) -> str | None:
        usage = self.coordinator.nakordoni_account_usage
        if usage is None or usage.pass_active is None:
            return None
        return "active" if usage.pass_active else "inactive"


class OverviewSensor(CoordinatorEntity[MobileFuelStationsCoordinator], SensorEntity):
    """Number of current nearby stations."""

    _attr_icon = "mdi:gas-station"
    _attr_name = "Nearby Stations"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_nearby_stations"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])

    @property
    def available(self) -> bool:
        # A real empty provider response is [] and remains state 0.  None is
        # reserved for missing GPS or a provider failure before any result.
        return self.coordinator.data is not None and super().available

    @property
    def extra_state_attributes(self):
        ref = self.coordinator.reference_position
        return {
            "radius": self.coordinator.config["radius"],
            "fuel_type": self.coordinator.config["fuel_type"],
            "fuel_types": getattr(self.coordinator, "fuel_types", [self.coordinator.config["fuel_type"]]),
            "location_entity": self.coordinator.config["location_entity"],
            "station_count": len(self.coordinator.data or []),
            "station_entities": _registered_station_entity_ids(
                self.hass, self._entry, int(self.coordinator.config[CONF_STATION_COUNT])
            ),
            "config_entry_id": self._entry.entry_id,
            "fetch_mode": getattr(self.coordinator, "fetch_mode", "automatic"),
            "last_successful_update": self.coordinator.last_successful_update.isoformat()
            if self.coordinator.last_successful_update
            else None,
            "last_update_attempt": getattr(self.coordinator, "last_update_attempt", None).isoformat()
            if getattr(self.coordinator, "last_update_attempt", None)
            else None,
            "last_update_success": getattr(self.coordinator, "last_update_success", None),
            "data_stale": getattr(self.coordinator, "data_stale", False),
            "data_age_seconds": getattr(self.coordinator, "data_age_seconds", None),
            "adaptive_updates": getattr(self.coordinator, "adaptive_updates_enabled", False),
            "adaptive_interval_minutes": (
                self.coordinator.update_interval.total_seconds() / 60
                if getattr(self.coordinator, "adaptive_updates_enabled", False)
                and getattr(self.coordinator, "update_interval", None)
                else None
            ),
            "last_gps_speed_kmh": getattr(
                getattr(self.coordinator, "last_gps_sample", None), "speed_kmh", None
            ),
            "last_update_error_at": getattr(self.coordinator, "last_update_error_at", None).isoformat()
            if getattr(self.coordinator, "last_update_error_at", None)
            else None,
            "last_update_error_class": getattr(self.coordinator, "last_update_error_class", None),
            "last_update_error_code": getattr(self.coordinator, "last_update_error_code", None),
            "last_update_error_provider": getattr(self.coordinator, "last_update_error_provider", None),
            "stale_price_count": sum(
                1 for station in (self.coordinator.data or []) if getattr(station, "price_stale", None) is True
            ),
            "last_update_result": getattr(self.coordinator, "last_update_result", None),
            "last_retry_after": getattr(self.coordinator, "last_retry_after", None),
            "provider_cooldown_remaining": getattr(
                self.coordinator, "diagnostic_provider_cooldown_remaining", 0
            ),
            "provider_cooldowns": getattr(
                self.coordinator, "diagnostic_provider_cooldowns", {}
            ),
            "provider_quotas": getattr(
                self.coordinator, "diagnostic_provider_quotas", {}
            ),
            "provider_availability": getattr(
                self.coordinator, "diagnostic_provider_availability", {}
            ),
            "manual_refresh_available": getattr(
                self.coordinator, "diagnostic_manual_refresh_available", False
            ),
            "manual_refresh_retry_seconds": getattr(
                self.coordinator, "diagnostic_manual_refresh_retry_seconds", 0
            ),
            "manual_refresh_blocked_reason": getattr(
                self.coordinator, "diagnostic_manual_refresh_blocked_reason", None
            ),
            "country_context": getattr(
                self.coordinator, "diagnostic_country_context", {}
            ),
            "next_provider": getattr(
                self.coordinator, "diagnostic_next_provider", None
            ),
            "recovery_status": getattr(self.coordinator, "recovery_status", "never"),
            "consecutive_failures": getattr(self.coordinator, "consecutive_failures", 0),
            "reference_latitude": ref[0] if ref else None,
            "reference_longitude": ref[1] if ref else None,
            "distance_since_last_search": self.coordinator.current_distance_km,
            "nearest_station": station_attributes(self.coordinator.nearest_station),
            "cheapest_station": station_attributes(self.coordinator.cheapest_station),
            "cheapest_stations_by_fuel": {
                fuel: station_attributes(station)
                for fuel, station in getattr(self.coordinator, "cheapest_stations", {}).items()
            },
            "provider": self.coordinator.config.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG),
            "configured_providers": sorted(getattr(self.coordinator, "provider_modes", ())),
            "fallback_attempted": getattr(self.coordinator, "fallback_attempted", False),
            "fallback_provider": getattr(self.coordinator, "fallback_provider", None),
            "fallback_result": getattr(self.coordinator, "fallback_result", None),
            "fallback_skip_reason": getattr(self.coordinator, "fallback_skip_reason", None),
            "attribution_name": "Data by nakordoni.eu"
            if self.coordinator.config.get(CONF_PROVIDER_MODE) == PROVIDER_NAKORDONI
            else None,
            "attribution_url": "https://nakordoni.eu"
            if self.coordinator.config.get(CONF_PROVIDER_MODE) == PROVIDER_NAKORDONI
            else None,
        }


class StationSlotSensor(CoordinatorEntity[MobileFuelStationsCoordinator], SensorEntity):
    """A stable slot containing the station currently assigned to it."""

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
    def name(self) -> str:
        """Expose the current station name without changing the stable entity identity."""
        return self.station.name if self.station and self.station.name else f"Station {self.index + 1}"

    @property
    def native_value(self) -> float | None:
        return self.station.price if self.station else None

    @property
    def native_unit_of_measurement(self) -> str:
        return f"{self.station.currency}/L" if self.station and self.station.currency else "EUR/L"

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
        attributes = {
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
        optional = {
            "currency": station.currency,
            "provider": station.provider,
            "price_updated_at": station.price_updated_at.isoformat() if station.price_updated_at else None,
            "price_confirmed_at": station.price_confirmed_at.isoformat() if station.price_confirmed_at else None,
            "price_age_hours": station.price_age_hours,
            "price_stale": station.price_stale,
            "fuel_type": station.fuel_type,
            "requested_fuel": station.requested_fuel,
            "fallback_used": station.fallback_used,
            "fuel_prices": station.fuel_prices,
            "fuel_fallbacks": station.fuel_fallbacks,
        }
        attributes.update({
            key: value
            for key, value in optional.items()
            if value is not None and (key != "fallback_used" or value)
        })
        if getattr(self.coordinator, "data_stale", False):
            attributes["price_stale"] = True
            attributes["data_stale"] = True
            attributes["data_age_hours"] = (
                self.coordinator.data_age_seconds / 3600
                if getattr(self.coordinator, "data_age_seconds", None) is not None else None
            )
        return attributes
