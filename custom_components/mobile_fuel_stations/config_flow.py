"""Config and options flows."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    CONF_API_KEY,
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_COOLDOWN,
    DEFAULT_FUEL_TYPE,
    DEFAULT_MOVEMENT_THRESHOLD,
    DEFAULT_MOVEMENT_UPDATES,
    DEFAULT_RADIUS,
    DEFAULT_STATION_COUNT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MIN_UPDATE_INTERVAL,
)


def _schema(defaults: dict[str, Any], include_key: bool) -> vol.Schema:
    schema: dict[Any, Any] = {}
    if include_key:
        schema[vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, ""))] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        )
    schema.update(
        {
            vol.Required(CONF_LOCATION_ENTITY, default=defaults.get(CONF_LOCATION_ENTITY, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["device_tracker", "sensor"])
            ),
            vol.Required(CONF_RADIUS, default=defaults.get(CONF_RADIUS, DEFAULT_RADIUS)): vol.All(
                vol.Coerce(float), vol.Range(min=1, max=100)
            ),
            vol.Required(CONF_FUEL_TYPE, default=defaults.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)): vol.In(
                ["diesel", "e5", "e10"]
            ),
            vol.Required(CONF_STATION_COUNT, default=defaults.get(CONF_STATION_COUNT, DEFAULT_STATION_COUNT)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=10)
            ),
            vol.Required(CONF_UPDATE_INTERVAL, default=defaults.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL, max=1440)
            ),
            vol.Required(CONF_MOVEMENT_UPDATES, default=defaults.get(CONF_MOVEMENT_UPDATES, DEFAULT_MOVEMENT_UPDATES)): bool,
            vol.Required(CONF_MOVEMENT_THRESHOLD, default=defaults.get(CONF_MOVEMENT_THRESHOLD, DEFAULT_MOVEMENT_THRESHOLD)): vol.All(
                vol.Coerce(float), vol.Range(min=0.1, max=100)
            ),
            vol.Required(CONF_COOLDOWN, default=defaults.get(CONF_COOLDOWN, DEFAULT_COOLDOWN)): vol.All(
                vol.Coerce(int), vol.Range(min=5, max=1440)
            ),
        }
    )
    return vol.Schema(schema)


def _validate_location(hass: HomeAssistant, entity_id: str) -> bool:
    state = hass.states.get(entity_id)
    if state is None:
        return False
    try:
        lat, lon = float(state.attributes.get("latitude")), float(state.attributes.get("longitude"))
    except (TypeError, ValueError):
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180


class MobileFuelStationsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input[CONF_API_KEY].strip():
                errors[CONF_API_KEY] = "api_key_required"
            elif not _validate_location(self.hass, user_input[CONF_LOCATION_ENTITY]):
                errors[CONF_LOCATION_ENTITY] = "invalid_location"
            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_LOCATION_ENTITY]}_{user_input[CONF_FUEL_TYPE]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Mobile Fuel Stations ({user_input[CONF_LOCATION_ENTITY]})",
                    data={CONF_API_KEY: user_input.pop(CONF_API_KEY), **user_input},
                )
        defaults = {CONF_RADIUS: DEFAULT_RADIUS, CONF_FUEL_TYPE: DEFAULT_FUEL_TYPE, CONF_STATION_COUNT: DEFAULT_STATION_COUNT,
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL, CONF_MOVEMENT_UPDATES: DEFAULT_MOVEMENT_UPDATES,
                    CONF_MOVEMENT_THRESHOLD: DEFAULT_MOVEMENT_THRESHOLD, CONF_COOLDOWN: DEFAULT_COOLDOWN}
        return self.async_show_form(step_id="user", data_schema=_schema(defaults, True), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow; HA provides ``config_entry`` on the flow."""
        return MobileFuelStationsOptionsFlow()


class MobileFuelStationsOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=_schema({**self.config_entry.data, **self.config_entry.options}, False))
