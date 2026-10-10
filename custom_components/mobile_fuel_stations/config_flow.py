"""Config and options flows."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .const import (
    CONFIG_ENTRY_VERSION,
    CONF_API_KEY,
    CONF_PETROMAP_API_KEY,
    CONF_PETROMAP_PRIVACY_ACCEPTED,
    CONF_NAKORDONI_API_KEY,
    CONF_NAKORDONI_PRIVACY_ACCEPTED,
    CONF_TANKERKOENIG_API_KEY,
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_FUEL_TYPES,
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
    DEFAULT_SORT_MODE,
    FUEL_TYPES,
    FUEL_TYPE_LABELS,
    DOMAIN,
    MIN_UPDATE_INTERVAL,
    MAX_API_RADIUS_KM,
    CONF_PROVIDER_MODE,
    CONF_SORT_FUEL,
    CONF_SORT_MODE,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
    PROVIDER_NAKORDONI,
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
    selected_fuels = _normalize_fuel_types(
        defaults.get(CONF_FUEL_TYPES, defaults.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE))
    )
    sort_fuel_default = defaults.get(CONF_SORT_FUEL, selected_fuels[0])
    if sort_fuel_default not in selected_fuels:
        sort_fuel_default = selected_fuels[0]
    if include_provider:
        schema[vol.Required(CONF_PROVIDER_MODE, default=defaults.get(CONF_PROVIDER_MODE, PROVIDER_AUTO))] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP, PROVIDER_NAKORDONI, PROVIDER_AUTO]
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
            # Keep the historical key for storage/entity compatibility while
            # allowing the selector to return multiple fuel types.
            vol.Required(
                CONF_FUEL_TYPE,
                default=_normalize_fuel_types(
                    defaults.get(CONF_FUEL_TYPES, defaults.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE))
                ),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[{"value": fuel, "label": label} for fuel, label in FUEL_TYPE_LABELS.items()],
                    multiple=True,
                )
            ),
            vol.Required(CONF_STATION_COUNT, default=defaults.get(CONF_STATION_COUNT, DEFAULT_STATION_COUNT)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, max=10, step=1, mode=selector.NumberSelectorMode.SLIDER
                )
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
            vol.Required(CONF_SORT_MODE, default=defaults.get(CONF_SORT_MODE, DEFAULT_SORT_MODE)): selector.SelectSelector(
                selector.SelectSelectorConfig(options=["distance", "price"])
            ),
            vol.Required(CONF_SORT_FUEL, default=sort_fuel_default): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(selected_fuels))
            ),
        }
    )
    return vol.Schema(schema)


def _normalize_fuel_types(value: object) -> list[str]:
    """Normalize legacy scalar and new multi-select values."""

    values = [value] if isinstance(value, str) else value if isinstance(value, (list, tuple, set)) else []
    result: list[str] = []
    for fuel in values:
        if isinstance(fuel, str) and fuel in FUEL_TYPES and fuel not in result:
            result.append(fuel)
    return result or [DEFAULT_FUEL_TYPE]


def _stored_fuel_value(value: object) -> str | list[str]:
    """Store one fuel as the legacy scalar, multiple fuels as a list."""

    fuels = _normalize_fuel_types(value)
    return fuels[0] if len(fuels) == 1 else fuels


def _normalize_sorting_input(values: dict[str, Any]) -> dict[str, Any]:
    """Keep the stored price-sort fuel valid for the selected fuels."""

    normalized = dict(values)
    selected_fuels = _normalize_fuel_types(
        normalized.get(CONF_FUEL_TYPES, normalized.get(CONF_FUEL_TYPE))
    )
    normalized[CONF_SORT_MODE] = normalized.get(CONF_SORT_MODE, DEFAULT_SORT_MODE)
    if normalized[CONF_SORT_MODE] not in ("distance", "price"):
        normalized[CONF_SORT_MODE] = DEFAULT_SORT_MODE
    if len(selected_fuels) == 1 or normalized.get(CONF_SORT_FUEL) not in selected_fuels:
        normalized[CONF_SORT_FUEL] = selected_fuels[0]
    return normalized


def _credential_schema(provider_mode: str) -> vol.Schema:
    """Return the provider-specific credential form."""

    if provider_mode == PROVIDER_AUTO:
        fields = {
            vol.Required(CONF_TANKERKOENIG_API_KEY): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
            vol.Required(CONF_PETROMAP_API_KEY): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
        }
    elif provider_mode == PROVIDER_NAKORDONI:
        fields = {
            vol.Required(CONF_NAKORDONI_API_KEY): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            )
        }
    else:
        fields = {
            vol.Required(CONF_API_KEY): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            )
        }
    return vol.Schema(fields)


def _options_credential_schema(provider_mode: str, missing: set[str]) -> vol.Schema:
    """Return password fields only for credentials missing from a target mode."""

    fields: dict[Any, Any] = {}
    for key in missing:
        fields[vol.Required(key)] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        )
    return vol.Schema(fields)


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

    VERSION = CONFIG_ENTRY_VERSION

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

    async def _async_create_user_entry(self, user_input):
        """Collect credentials and create the entry if the provider is enabled."""

        user_input = _normalize_sorting_input(user_input)
        provider_mode = user_input.get(CONF_PROVIDER_MODE, PROVIDER_AUTO)
        api_key = user_input.get(CONF_API_KEY, "").strip()
        if provider_mode == PROVIDER_PETROMAP:
            api_key = user_input.get(CONF_PETROMAP_API_KEY, api_key).strip()
        elif provider_mode == PROVIDER_NAKORDONI:
            api_key = user_input.get(CONF_NAKORDONI_API_KEY, api_key).strip()
        errors = {}
        if provider_mode == PROVIDER_AUTO:
            tankerkoenig_key = user_input.get(CONF_TANKERKOENIG_API_KEY, "").strip()
            petromap_key = user_input.get(CONF_PETROMAP_API_KEY, "").strip()
            if not tankerkoenig_key:
                errors[CONF_TANKERKOENIG_API_KEY] = "api_key_required"
            if not petromap_key:
                errors[CONF_PETROMAP_API_KEY] = "api_key_required"
            if not errors and PROVIDER_REGISTRY.get(PROVIDER_PETROMAP) is None:
                errors["base"] = "unknown"
        elif provider_mode in (PROVIDER_PETROMAP, PROVIDER_NAKORDONI):
            if not api_key:
                errors_key = CONF_PETROMAP_API_KEY if provider_mode == PROVIDER_PETROMAP else CONF_NAKORDONI_API_KEY
                errors[errors_key] = "api_key_required"
            registration = PROVIDER_REGISTRY.get(provider_mode)
            if not errors and registration is None:
                errors["base"] = "unknown"
            elif not errors and (not registration.enabled or registration.factory is None):
                errors["base"] = "provider_disabled"
        if errors:
            step_id = {
                PROVIDER_AUTO: "auto_credentials",
                PROVIDER_NAKORDONI: "nakordoni_credentials",
                PROVIDER_TANKERKOENIG: "tankerkoenig_credentials",
            }.get(provider_mode, "petromap_credentials")
            return self.async_show_form(
                step_id=step_id,
                data_schema=_credential_schema(provider_mode),
                errors=errors,
            )
        selected_fuels = _normalize_fuel_types(user_input.get(CONF_FUEL_TYPE))
        await self.async_set_unique_id(
            f"{user_input[CONF_LOCATION_ENTITY]}_{'-'.join(selected_fuels)}"
        )
        self._abort_if_unique_id_configured()
        data = dict(user_input)
        data[CONF_FUEL_TYPE] = _stored_fuel_value(selected_fuels)
        data[CONF_FUEL_TYPES] = selected_fuels
        data[CONF_PROVIDER_MODE] = provider_mode
        if provider_mode == PROVIDER_AUTO:
            data.pop(CONF_API_KEY, None)
            data[CONF_TANKERKOENIG_API_KEY] = user_input[CONF_TANKERKOENIG_API_KEY].strip()
            data[CONF_PETROMAP_API_KEY] = user_input[CONF_PETROMAP_API_KEY].strip()
            data[CONF_PETROMAP_PRIVACY_ACCEPTED] = True
        elif provider_mode == PROVIDER_PETROMAP:
            data.pop(CONF_API_KEY, None)
            data[CONF_PETROMAP_API_KEY] = api_key
            data[CONF_PETROMAP_PRIVACY_ACCEPTED] = True
        elif provider_mode == PROVIDER_NAKORDONI:
            data.pop(CONF_API_KEY, None)
            data[CONF_NAKORDONI_API_KEY] = api_key
            data[CONF_NAKORDONI_PRIVACY_ACCEPTED] = True
        else:
            data.pop(CONF_API_KEY, None)
            data[CONF_TANKERKOENIG_API_KEY] = api_key
        return self.async_create_entry(
            title=f"Mobile Fuel Stations ({user_input[CONF_LOCATION_ENTITY]})",
            data=data,
        )

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            provider_mode = user_input.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            if not _validate_location(self.hass, user_input[CONF_LOCATION_ENTITY]):
                errors[CONF_LOCATION_ENTITY] = "invalid_location"
            if not errors:
                self._pending_user_input = dict(user_input)
                if provider_mode == PROVIDER_PETROMAP:
                    return self.async_show_form(step_id="petromap_privacy", data_schema=vol.Schema({}))
                if provider_mode == PROVIDER_NAKORDONI:
                    return self.async_show_form(step_id="nakordoni_privacy", data_schema=vol.Schema({}))
                if provider_mode == PROVIDER_AUTO:
                    return self.async_show_form(step_id="auto_privacy", data_schema=vol.Schema({}))
                return self.async_show_form(
                    step_id="tankerkoenig_credentials",
                    data_schema=_credential_schema(PROVIDER_TANKERKOENIG),
                )
        defaults = {CONF_RADIUS: DEFAULT_RADIUS, CONF_FUEL_TYPE: DEFAULT_FUEL_TYPE, CONF_FUEL_TYPES: [DEFAULT_FUEL_TYPE], CONF_STATION_COUNT: DEFAULT_STATION_COUNT,
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL, CONF_MOVEMENT_UPDATES: DEFAULT_MOVEMENT_UPDATES,
                    CONF_MOVEMENT_THRESHOLD: DEFAULT_MOVEMENT_THRESHOLD, CONF_COOLDOWN: DEFAULT_COOLDOWN}
        return self.async_show_form(
            step_id="user", data_schema=_schema(defaults, False, True), errors=errors
        )

    async def async_step_petromap_privacy(self, user_input=None):
        """Show the Petromap data-transfer disclosure before validation."""

        if user_input is None:
            return self.async_show_form(
                step_id="petromap_privacy", data_schema=vol.Schema({})
            )
        return self.async_show_form(
            step_id="petromap_credentials",
            data_schema=_credential_schema(PROVIDER_PETROMAP),
        )

    async def async_step_auto_privacy(self, user_input=None):
        """Show the Auto/Petromap data-transfer disclosure before validation."""

        if user_input is None:
            return self.async_show_form(step_id="auto_privacy", data_schema=vol.Schema({}))
        return self.async_show_form(
            step_id="auto_credentials",
            data_schema=_credential_schema(PROVIDER_AUTO),
        )

    async def async_step_nakordoni_privacy(self, user_input=None):
        """Show the Nakordoni location-transfer disclosure before credentials."""

        if user_input is None:
            return self.async_show_form(step_id="nakordoni_privacy", data_schema=vol.Schema({}))
        return self.async_show_form(
            step_id="nakordoni_credentials",
            data_schema=_credential_schema(PROVIDER_NAKORDONI),
        )

    async def async_step_tankerkoenig_credentials(self, user_input=None):
        """Collect the explicit Tankerkönig credential without validation."""

        if user_input is None:
            return self.async_show_form(
                step_id="tankerkoenig_credentials",
                data_schema=_credential_schema(PROVIDER_TANKERKOENIG),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_petromap_credentials(self, user_input=None):
        """Collect the explicit Petromap credential without a setup request."""

        if user_input is None:
            return self.async_show_form(
                step_id="petromap_credentials",
                data_schema=_credential_schema(PROVIDER_PETROMAP),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_auto_credentials(self, user_input=None):
        """Collect both provider credentials without a setup request."""

        if user_input is None:
            return self.async_show_form(
                step_id="auto_credentials",
                data_schema=_credential_schema(PROVIDER_AUTO),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_nakordoni_credentials(self, user_input=None):
        """Collect the Nakordoni credential without a setup request."""

        if user_input is None:
            return self.async_show_form(
                step_id="nakordoni_credentials",
                data_schema=_credential_schema(PROVIDER_NAKORDONI),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_reauth(self, entry_data):
        """Start reauthentication for an explicit or Auto Petromap entry."""

        if self.context.get("provider_mode") == PROVIDER_NAKORDONI:
            return await self.async_step_reauth_nakordoni_confirm()
        if self.context.get("provider_mode") == PROVIDER_PETROMAP and entry_data.get(
            CONF_PROVIDER_MODE
        ) == PROVIDER_AUTO:
            return await self.async_step_reauth_auto_confirm()
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_nakordoni_confirm(self, user_input=None):
        """Replace only the Nakordoni credential without a network request."""

        errors = {}
        if user_input is not None:
            api_key = user_input.get(CONF_NAKORDONI_API_KEY, "").strip()
            reauth_entry = self._get_reauth_entry()
            if not api_key:
                errors[CONF_NAKORDONI_API_KEY] = "api_key_required"
            elif reauth_entry is None:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_NAKORDONI_API_KEY: api_key},
                )
        return self.async_show_form(
            step_id="reauth_nakordoni_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_NAKORDONI_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                )
            }),
            errors=errors,
        )

    async def async_step_reauth_auto_confirm(self, user_input=None):
        """Replace only the Auto Petromap credential without a usage request."""

        errors = {}
        if user_input is not None:
            api_key = user_input.get(CONF_PETROMAP_API_KEY, "").strip()
            reauth_entry = self._get_reauth_entry()
            if not api_key:
                errors[CONF_PETROMAP_API_KEY] = "api_key_required"
            elif reauth_entry is None:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_PETROMAP_API_KEY: api_key},
                )
        return self.async_show_form(
            step_id="reauth_auto_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PETROMAP_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_reauth_confirm(self, user_input=None):
        """Replace only the explicit Petromap credential without a usage request."""

        errors = {}
        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY, "").strip()
            reauth_entry = self._get_reauth_entry()
            if not api_key:
                errors[CONF_API_KEY] = "api_key_required"
            elif reauth_entry is None:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_PETROMAP_API_KEY: api_key},
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
            self._pending_options = _normalize_sorting_input(user_input)
            current_mode = self.config_entry.data.get(
                CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG
            )
            target_mode = user_input.get(CONF_PROVIDER_MODE, current_mode)
            if target_mode in (PROVIDER_PETROMAP, PROVIDER_AUTO) and not self.config_entry.data.get(
                CONF_PETROMAP_PRIVACY_ACCEPTED, False
            ):
                return self.async_show_form(
                    step_id="options_petromap_privacy", data_schema=vol.Schema({})
                )
            if target_mode == PROVIDER_NAKORDONI and not self.config_entry.data.get(
                CONF_NAKORDONI_PRIVACY_ACCEPTED, False
            ):
                return self.async_show_form(
                    step_id="options_nakordoni_privacy", data_schema=vol.Schema({})
                )
            return await self._async_options_credentials({})
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                {**self.config_entry.data, **self.config_entry.options},
                False,
                True,
            ),
        )

    async def async_step_options_petromap_privacy(self, user_input=None):
        """Show the Petromap disclosure before a provider switch activates it."""

        if user_input is None:
            return self.async_show_form(
                step_id="options_petromap_privacy", data_schema=vol.Schema({})
            )
        self._petromap_privacy_accepted = True
        return await self._async_options_credentials({})

    async def async_step_options_nakordoni_privacy(self, user_input=None):
        """Show the Nakordoni location-transfer disclosure before activation."""

        if user_input is None:
            return self.async_show_form(
                step_id="options_nakordoni_privacy", data_schema=vol.Schema({})
            )
        self._nakordoni_privacy_accepted = True
        return await self._async_options_credentials({})

    async def async_step_provider_credentials(self, user_input=None):
        """Collect only credentials missing for the selected provider mode."""

        return await self._async_options_credentials(user_input or {})

    async def _async_options_credentials(self, credentials: dict[str, Any]):
        pending = getattr(self, "_pending_options", {})
        current_data = dict(self.config_entry.data)
        current_mode = current_data.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
        target_mode = pending.get(CONF_PROVIDER_MODE, current_mode)

        source_tankerkoenig_key = current_data.get(CONF_TANKERKOENIG_API_KEY, "")
        source_petromap_key = current_data.get(CONF_PETROMAP_API_KEY, "")
        source_nakordoni_key = current_data.get(CONF_NAKORDONI_API_KEY, "")
        legacy_api_key = current_data.get(CONF_API_KEY, "")
        legacy_key_is_unambiguous = False
        if current_mode in (None, PROVIDER_TANKERKOENIG) and not source_tankerkoenig_key:
            source_tankerkoenig_key = legacy_api_key
            legacy_key_is_unambiguous = bool(legacy_api_key)
        if current_mode == PROVIDER_PETROMAP and not source_petromap_key:
            source_petromap_key = legacy_api_key
            legacy_key_is_unambiguous = bool(legacy_api_key)

        tankerkoenig_key = source_tankerkoenig_key
        petromap_key = source_petromap_key
        nakordoni_key = source_nakordoni_key
        missing: set[str] = set()
        if target_mode == PROVIDER_AUTO:
            tankerkoenig_key = credentials.get(CONF_TANKERKOENIG_API_KEY, "").strip()
            petromap_key = credentials.get(CONF_PETROMAP_API_KEY, "").strip()
            if not tankerkoenig_key:
                tankerkoenig_key = source_tankerkoenig_key
            if not petromap_key:
                petromap_key = source_petromap_key
            if not tankerkoenig_key:
                missing.add(CONF_TANKERKOENIG_API_KEY)
            if not petromap_key:
                missing.add(CONF_PETROMAP_API_KEY)
        elif target_mode == PROVIDER_PETROMAP:
            api_key = (
                credentials.get(CONF_PETROMAP_API_KEY)
                or credentials.get(CONF_API_KEY, "")
            ).strip()
            if not api_key:
                api_key = source_petromap_key
            if not api_key:
                missing.add(CONF_PETROMAP_API_KEY)
        elif target_mode == PROVIDER_NAKORDONI:
            api_key = credentials.get(CONF_NAKORDONI_API_KEY, "").strip()
            if not api_key:
                api_key = source_nakordoni_key
            if not api_key:
                missing.add(CONF_NAKORDONI_API_KEY)
        else:
            api_key = (
                credentials.get(CONF_TANKERKOENIG_API_KEY)
                or credentials.get(CONF_API_KEY, "")
            ).strip()
            if not api_key:
                api_key = source_tankerkoenig_key
            if not api_key:
                missing.add(CONF_TANKERKOENIG_API_KEY)

        if missing:
            return self.async_show_form(
                step_id="provider_credentials",
                data_schema=_options_credential_schema(target_mode, missing),
                errors={key: "api_key_required" for key in missing},
            )

        new_data = {
            key: value
            for key, value in current_data.items()
            if key
            not in {
                CONF_API_KEY,
                CONF_TANKERKOENIG_API_KEY,
                CONF_PETROMAP_API_KEY,
                CONF_NAKORDONI_API_KEY,
            }
        }
        new_data[CONF_PROVIDER_MODE] = target_mode
        if target_mode == PROVIDER_PETROMAP:
            petromap_key = api_key
        elif target_mode == PROVIDER_TANKERKOENIG:
            tankerkoenig_key = api_key
        elif target_mode == PROVIDER_NAKORDONI:
            nakordoni_key = api_key
        if tankerkoenig_key:
            new_data[CONF_TANKERKOENIG_API_KEY] = tankerkoenig_key
        if petromap_key:
            new_data[CONF_PETROMAP_API_KEY] = petromap_key
        if nakordoni_key:
            new_data[CONF_NAKORDONI_API_KEY] = nakordoni_key
        if legacy_api_key and not legacy_key_is_unambiguous:
            # Preserve an unexpected generic key until its provider can be
            # identified; dropping it here could destroy a user's credential.
            new_data[CONF_API_KEY] = legacy_api_key
        if current_data.get(CONF_PETROMAP_PRIVACY_ACCEPTED, False) or getattr(
            self, "_petromap_privacy_accepted", False
        ):
            new_data[CONF_PETROMAP_PRIVACY_ACCEPTED] = True
        elif CONF_PETROMAP_PRIVACY_ACCEPTED in current_data:
            new_data[CONF_PETROMAP_PRIVACY_ACCEPTED] = current_data[
                CONF_PETROMAP_PRIVACY_ACCEPTED
            ]
        if current_data.get(CONF_NAKORDONI_PRIVACY_ACCEPTED, False) or getattr(
            self, "_nakordoni_privacy_accepted", False
        ):
            new_data[CONF_NAKORDONI_PRIVACY_ACCEPTED] = True
        elif CONF_NAKORDONI_PRIVACY_ACCEPTED in current_data:
            new_data[CONF_NAKORDONI_PRIVACY_ACCEPTED] = current_data[
                CONF_NAKORDONI_PRIVACY_ACCEPTED
            ]

        options = {
            key: value
            for key, value in pending.items()
            if key
            not in {
                CONF_PROVIDER_MODE,
                CONF_API_KEY,
                CONF_TANKERKOENIG_API_KEY,
                CONF_PETROMAP_API_KEY,
                CONF_NAKORDONI_API_KEY,
            }
        }
        if CONF_FUEL_TYPE in pending or CONF_FUEL_TYPES in pending:
            selected_fuels = _normalize_fuel_types(
                pending.get(CONF_FUEL_TYPES, pending.get(CONF_FUEL_TYPE))
            )
            options[CONF_FUEL_TYPE] = _stored_fuel_value(selected_fuels)
            options[CONF_FUEL_TYPES] = selected_fuels
        # Update data and options together.  The OptionsFlowManager applies the
        # returned options mapping after this step; passing the same mapping here
        # makes the entry update atomic and prevents the update listener from
        # reloading a coordinator with a half-applied configuration.
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=new_data,
            options=options,
        )
        return self.async_create_entry(title="", data=options)
