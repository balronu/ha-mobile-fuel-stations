"""Diagnostics with secrets and exact coordinates excluded."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_API_KEY,
    CONF_NAKORDONI_API_KEY,
    CONF_PETROMAP_API_KEY,
    CONF_TANKERKOENIG_API_KEY,
)


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = entry.runtime_data
    return {
        "version": 1,
        "config": {
            key: value
            for key, value in {**entry.data, **entry.options}.items()
            if key not in {
                CONF_API_KEY,
                CONF_TANKERKOENIG_API_KEY,
                CONF_PETROMAP_API_KEY,
                CONF_NAKORDONI_API_KEY,
            }
            and "coordinate" not in key
            and key not in {"latitude", "longitude"}
        },
        "runtime": {
            "gps_available": coordinator.current_distance_km is not None,
            "last_successful_update": coordinator.last_successful_update.isoformat() if coordinator.last_successful_update else None,
            "result_count": len(coordinator.data or []),
            "error": str(coordinator.last_exception) if coordinator.last_exception else None,
        },
    }
