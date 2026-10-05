"""Mobile Fuel Stations integration."""

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import MobileFuelStationsCoordinator

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
type MobileFuelStationsConfigEntry = ConfigEntry[MobileFuelStationsCoordinator]

_FRONTEND_DIR = Path(__file__).parent / "frontend"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration-wide frontend path once per HA instance."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("frontend_registered"):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(f"/{DOMAIN}", str(_FRONTEND_DIR), True)]
        )
        domain_data["frontend_registered"] = True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MobileFuelStationsConfigEntry) -> bool:
    coordinator = MobileFuelStationsCoordinator(hass, entry)
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MobileFuelStationsConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and entry.runtime_data:
        await entry.runtime_data.async_shutdown()
    return unloaded
