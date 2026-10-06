"""Config and options flows."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
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
    MAX_API_RADIUS_KM,
    CONF_PROVIDER_MODE,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
)
from .providers import PROVIDER_REGISTRY
from .providers.base import (
    ProviderAuthError,
    ProviderDailyBudgetError,
    ProviderError,
    ProviderInsufficientCreditsError,
    ProviderNetworkError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from .providers.petromap import async_validate_petromap_credentials


def _schema(
    defaults: dict[str, Any], include_key: bool, include_provider: bool = False
) -> vol.Schema:
    schema: dict[Any, Any] = {}
    radius_default = min(float(defaults.get(CONF_RADIUS, DEFAULT_RADIUS)), MAX_API_RADIUS_KM)
    if include_provider:
        schema[vol.Required(CONF_PROVIDER_MODE, default=defaults.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG))] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP, PROVIDER_AUTO]
            )
        )
    if include_key:
        schema[vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, ""))] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        )
    schema.update(
        {
            vol.Required(CONF_LOCATION_ENTITY, default=defaults.get(CONF_LOCATION_ENTITY, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["device_tracker", "sensor"])
            ),
            vol.Required(CONF_RADIUS, default=radius_default): vol.All(
                vol.Coerce(float), vol.Range(min=1, max=MAX_API_RADIUS_KM)
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

    @staticmethod
    def _validation_error(error: ProviderError) -> str:
        if isinstance(error, ProviderAuthError):
            return "invalid_auth"
        if isinstance(error, ProviderPermissionError):
            return "permission_error"
        if isinstance(error, ProviderRateLimitError):
            return "rate_limited"
        if isinstance(error, (ProviderDailyBudgetError, ProviderInsufficientCreditsError)):
            return "budget_exhausted"
        if isinstance(error, (ProviderTimeoutError, ProviderNetworkError, ProviderUnavailableError)):
            return "cannot_connect"
        if isinstance(error, ProviderResponseError):
            return "unknown"
        return "unknown"

    async def _validate_petromap_key(self, api_key: str) -> str | None:
        try:
            await async_validate_petromap_credentials(
                async_get_clientsession(self.hass), api_key
            )
        except ProviderError as err:
            return self._validation_error(err)
        return None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            provider_mode = user_input.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            api_key = user_input.get(CONF_API_KEY, "").strip()
            if not api_key:
                errors[CONF_API_KEY] = "api_key_required"
            elif not _validate_location(self.hass, user_input[CONF_LOCATION_ENTITY]):
                errors[CONF_LOCATION_ENTITY] = "invalid_location"
            elif provider_mode in (PROVIDER_PETROMAP, PROVIDER_AUTO):
                registration = PROVIDER_REGISTRY.get(provider_mode)
                validation_error = await self._validate_petromap_key(api_key)
                if validation_error:
                    errors["base"] = validation_error
                elif registration is None:
                    errors["base"] = "unknown"
                elif not registration.enabled or registration.factory is None:
                    errors["base"] = "provider_disabled"
            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_LOCATION_ENTITY]}_{user_input[CONF_FUEL_TYPE]}"
                )
                self._abort_if_unique_id_configured()
                data = dict(user_input)
                data[CONF_PROVIDER_MODE] = provider_mode
                data[CONF_API_KEY] = api_key
                return self.async_create_entry(
                    title=f"Mobile Fuel Stations ({user_input[CONF_LOCATION_ENTITY]})",
                    data=data,
                )
        defaults = {CONF_RADIUS: DEFAULT_RADIUS, CONF_FUEL_TYPE: DEFAULT_FUEL_TYPE, CONF_STATION_COUNT: DEFAULT_STATION_COUNT,
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL, CONF_MOVEMENT_UPDATES: DEFAULT_MOVEMENT_UPDATES,
                    CONF_MOVEMENT_THRESHOLD: DEFAULT_MOVEMENT_THRESHOLD, CONF_COOLDOWN: DEFAULT_COOLDOWN}
        return self.async_show_form(
            step_id="user", data_schema=_schema(defaults, True, True), errors=errors
        )

    async def async_step_reauth(self, entry_data):
        """Start reauthentication for a Petromap entry."""

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Replace only the Petromap credential after successful validation."""

        errors = {}
        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY, "").strip()
            reauth_entry = self._get_reauth_entry()
            if not api_key:
                errors[CONF_API_KEY] = "api_key_required"
            elif reauth_entry is None:
                errors["base"] = "unknown"
            else:
                validation_error = await self._validate_petromap_key(api_key)
                if validation_error:
                    errors["base"] = validation_error
                else:
                    return self.async_update_reload_and_abort(
                        reauth_entry,
                        data_updates={CONF_API_KEY: api_key},
                    )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    )
                }
            ),
            errors=errors,
        )

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
