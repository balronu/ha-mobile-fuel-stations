"""Mobile Fuel Stations integration."""

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, FRONTEND_URL
from .coordinator import MobileFuelStationsCoordinator
from .providers.base import FuelFallbackBlockedError, NoSuitableProviderError

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
type MobileFuelStationsConfigEntry = ConfigEntry[MobileFuelStationsCoordinator]

_FRONTEND_DIR = Path(__file__).parent / "frontend"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration-wide frontend path once per HA instance."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("frontend_registered"):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(f"/{DOMAIN}", str(_FRONTEND_DIR), False)]
        )
        add_extra_js_url(hass, FRONTEND_URL)
        domain_data["frontend_registered"] = True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MobileFuelStationsConfigEntry) -> bool:
    coordinator = MobileFuelStationsCoordinator(hass, entry)
    await coordinator.async_setup()
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady as err:
        cause = err.__cause__
        while cause is not None and cause.__cause__ is not None:
            cause = cause.__cause__
        is_auto = entry.data.get("provider_mode") == "auto"
        if not (
            is_auto
            and isinstance(cause, (NoSuitableProviderError, FuelFallbackBlockedError))
        ):
            raise
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: MobileFuelStationsConfigEntry) -> None:
    """Reload the entry after options or credential data changes."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MobileFuelStationsConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and entry.runtime_data:
        await entry.runtime_data.async_shutdown()
    return unloaded
