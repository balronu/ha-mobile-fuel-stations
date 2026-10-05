"""Mobile Fuel Stations integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MobileFuelStationsCoordinator

PLATFORMS = [Platform.SENSOR]
type MobileFuelStationsConfigEntry = ConfigEntry[MobileFuelStationsCoordinator]


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
