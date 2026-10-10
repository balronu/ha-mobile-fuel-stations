"""Config and options flows."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from homeassistant.helpers.storage import Store

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
    CONF_MANAGE_CREDENTIALS,
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
    CONF_PROVIDER_MODES,
    CONF_PROVIDER_STATUS,
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

PROVIDER_CHOICES = (
    PROVIDER_TANKERKOENIG,
    PROVIDER_PETROMAP,
    PROVIDER_NAKORDONI,
)


def _normalize_provider_modes(value: object, fallback_mode: object = PROVIDER_TANKERKOENIG) -> list[str]:
    """Normalize the new provider multi-select and legacy provider mode."""

    values = [value] if isinstance(value, str) else value if isinstance(value, (list, tuple, set, frozenset)) else []
    result = [provider for provider in values if provider in PROVIDER_CHOICES]
    if result:
        return list(dict.fromkeys(result))
    if fallback_mode == PROVIDER_AUTO:
        # Legacy beta entries used Auto for Tankerkönig + Petromap.  Keep that
        # interpretation when an older test/entry has no provider_modes key.
        return [PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP]
    if fallback_mode in PROVIDER_CHOICES:
        return [fallback_mode]
    return [PROVIDER_TANKERKOENIG]


def _effective_provider_mode(provider_modes: list[str]) -> str:
    """Keep the legacy scalar mode as the runtime compatibility value."""

    return provider_modes[0] if len(provider_modes) == 1 else PROVIDER_AUTO


def _provider_key(provider: str) -> str:
    return {
        PROVIDER_TANKERKOENIG: CONF_TANKERKOENIG_API_KEY,
        PROVIDER_PETROMAP: CONF_PETROMAP_API_KEY,
        PROVIDER_NAKORDONI: CONF_NAKORDONI_API_KEY,
    }[provider]


def _schema(
    defaults: dict[str, Any], include_key: bool, include_provider: bool = False,
    include_credentials_management: bool = False,
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
        provider_modes = _normalize_provider_modes(
            defaults.get(CONF_PROVIDER_MODES), defaults.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
        )
        schema[vol.Required(CONF_PROVIDER_MODES, default=provider_modes)] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=list(PROVIDER_CHOICES),
                multiple=True,
                translation_key=CONF_PROVIDER_MODES,
            )
        )
    if include_credentials_management:
        schema[vol.Optional(CONF_MANAGE_CREDENTIALS, default=False)] = bool
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
                    translation_key=CONF_FUEL_TYPE,
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
                selector.SelectSelectorConfig(
                    options=["distance", "price"], translation_key=CONF_SORT_MODE
                )
            ),
            vol.Required(CONF_SORT_FUEL, default=sort_fuel_default): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(selected_fuels), translation_key=CONF_SORT_FUEL
                )
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
    provider_modes = _normalize_provider_modes(
        normalized.get(CONF_PROVIDER_MODES), normalized.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
    )
    normalized[CONF_PROVIDER_MODES] = provider_modes
    normalized[CONF_PROVIDER_MODE] = _effective_provider_mode(provider_modes)
    return normalized


def _credential_schema(provider_modes: list[str]) -> vol.Schema:
    """Return the provider-specific credential form."""

    fields: dict[Any, Any] = {}
    for provider in provider_modes:
        key = _provider_key(provider)
        fields[vol.Required(key)] = selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            )
    return vol.Schema(fields)


def _options_credential_schema(provider_modes: list[str], current_data: dict[str, Any]) -> vol.Schema:
    """Return safe replacement/removal controls for selected providers."""

    fields: dict[Any, Any] = {}
    for provider in provider_modes:
        key = _provider_key(provider)
        fields[vol.Optional(key, default="")] = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        )
        fields[vol.Optional(f"remove_{key}", default=False)] = bool
    return vol.Schema(fields)


_STATUS_LABELS = {
    "de": {
        "no_key": "Kein API-Schlüssel hinterlegt",
        "untested": "API-Schlüssel hinterlegt – noch nicht geprüft",
        "success": "Zugang erfolgreich geprüft",
        "auth_failed": "Authentifizierung fehlgeschlagen",
        "uncheckable": "Zugang derzeit nicht prüfbar",
        "approval_pending": "API-Freigabe ausstehend",
        "not_selected": "Nicht ausgewählt",
    },
    "en": {
        "no_key": "No API key stored",
        "untested": "API key stored – not checked yet",
        "success": "Access successfully checked",
        "auth_failed": "Authentication failed",
        "uncheckable": "Access cannot be checked right now",
        "approval_pending": "API approval pending",
        "not_selected": "Not selected",
    },
}

_PROVIDER_LABELS = {
    PROVIDER_TANKERKOENIG: "Tankerkönig",
    PROVIDER_PETROMAP: "Petromap",
    PROVIDER_NAKORDONI: "Nakordoni",
}


def _language(hass: HomeAssistant | None) -> str:
    language = getattr(getattr(hass, "config", None), "language", "en")
    return "de" if str(language).lower().startswith("de") else "en"


def _status_for_provider(hass: HomeAssistant | None, entry: Any, data: dict[str, Any], provider: str) -> str:
    modes = _normalize_provider_modes(data.get(CONF_PROVIDER_MODES), data.get(CONF_PROVIDER_MODE))
    if provider not in modes:
        return "not_selected"
    if not data.get(_provider_key(provider)):
        return "no_key"
    statuses = getattr(hass, "data", {}).get(DOMAIN, {}).get("provider_status", {}) if hass is not None else {}
    stored = statuses.get(entry.entry_id, {}).get(provider, {}) if entry is not None else {}
    return stored.get("status", "untested") if isinstance(stored, dict) else "untested"


def _credential_status_placeholders(data: dict[str, Any], hass: HomeAssistant | None = None, entry: Any = None) -> dict[str, str]:
    language = _language(hass)
    labels = _STATUS_LABELS[language]
    statuses = {
        provider: labels[_status_for_provider(hass, entry, data, provider)]
        for provider in PROVIDER_CHOICES
    }
    selected = _normalize_provider_modes(data.get(CONF_PROVIDER_MODES), data.get(CONF_PROVIDER_MODE))
    if len(selected) > 1:
        mode_status = "Automatic provider selection active" if language == "en" else "Automatische Anbieterauswahl aktiv"
    else:
        mode_status = "Only the selected provider is used" if language == "en" else "Es wird ausschließlich der ausgewählte Anbieter verwendet"
    status_line = " · ".join(f"{_PROVIDER_LABELS[provider]}: {statuses[provider]}" for provider in PROVIDER_CHOICES)
    hint = "Credentials can be changed or removed in the credential manager." if language == "en" else "Zugangsdaten können unter Zugangsdaten verwalten geändert oder entfernt werden."
    return {
        **{f"{provider}_status": statuses[provider] for provider in PROVIDER_CHOICES},
        "provider_mode_status": mode_status,
        "provider_status": status_line,
        "credentials_hint": hint,
    }


async def _reset_provider_status(hass: HomeAssistant, entry_id: str, providers: set[str], data: dict[str, Any]) -> None:
    """Invalidate only providers whose credentials were explicitly changed."""

    if not hasattr(hass, "data"):
        return
    domain_data = hass.data.setdefault(DOMAIN, {})
    all_status = domain_data.setdefault("provider_status", {}).setdefault(entry_id, {})
    for provider in providers:
        all_status[provider] = {
            "status": "untested" if data.get(_provider_key(provider)) else "no_key",
        }
    await Store(hass, 1, f"{DOMAIN}.provider_status.{entry_id}").async_save(all_status)


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
        provider_modes = _normalize_provider_modes(
            user_input.get(CONF_PROVIDER_MODES), user_input.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
        )
        provider_mode = _effective_provider_mode(provider_modes)
        errors = {}
        credentials = {}
        for provider in provider_modes:
            key_name = _provider_key(provider)
            key = str(
                user_input.get(key_name)
                or (user_input.get(CONF_API_KEY, "") if len(provider_modes) == 1 else "")
            ).strip()
            credentials[key_name] = key
            if not key:
                errors[key_name] = "api_key_required"
            registration = PROVIDER_REGISTRY.get(provider)
            if registration is None:
                errors["base"] = "unknown"
            elif not registration.enabled or registration.factory is None:
                errors["base"] = "provider_disabled"
        if errors:
            return self.async_show_form(
                step_id="provider_credentials",
                data_schema=_credential_schema(provider_modes),
                errors=errors,
            )
        selected_fuels = _normalize_fuel_types(user_input.get(CONF_FUEL_TYPE))
        await self.async_set_unique_id(
            f"{user_input[CONF_LOCATION_ENTITY]}_{'-'.join(selected_fuels)}"
        )
        self._abort_if_unique_id_configured()
        data = dict(user_input)
        data.pop(CONF_PROVIDER_MODES, None)
        data[CONF_FUEL_TYPE] = _stored_fuel_value(selected_fuels)
        data[CONF_FUEL_TYPES] = selected_fuels
        data[CONF_PROVIDER_MODE] = provider_mode
        data[CONF_PROVIDER_MODES] = provider_modes
        data.pop(CONF_API_KEY, None)
        for key_name, key in credentials.items():
            data[key_name] = key
        if PROVIDER_PETROMAP in provider_modes:
            data[CONF_PETROMAP_PRIVACY_ACCEPTED] = True
        if PROVIDER_NAKORDONI in provider_modes:
            data[CONF_NAKORDONI_PRIVACY_ACCEPTED] = True
        return self.async_create_entry(
            title=f"Mobile Fuel Stations ({user_input[CONF_LOCATION_ENTITY]})",
            data=data,
        )

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            raw_provider_modes = user_input.get(CONF_PROVIDER_MODES)
            provider_modes = _normalize_provider_modes(
                raw_provider_modes, user_input.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
            )
            if isinstance(raw_provider_modes, (list, tuple, set, frozenset)) and not any(
                provider in PROVIDER_CHOICES for provider in raw_provider_modes
            ):
                errors[CONF_PROVIDER_MODES] = "provider_required"
            if not _validate_location(self.hass, user_input[CONF_LOCATION_ENTITY]):
                errors[CONF_LOCATION_ENTITY] = "invalid_location"
            if not errors:
                self._pending_user_input = _normalize_sorting_input(dict(user_input))
                legacy_mode = user_input.get(CONF_PROVIDER_MODE)
                if legacy_mode == PROVIDER_TANKERKOENIG and CONF_PROVIDER_MODES not in user_input:
                    return self.async_show_form(step_id="tankerkoenig_credentials", data_schema=_credential_schema([PROVIDER_TANKERKOENIG]))
                if legacy_mode == PROVIDER_PETROMAP and CONF_PROVIDER_MODES not in user_input:
                    return self.async_show_form(step_id="petromap_privacy", data_schema=vol.Schema({}))
                if legacy_mode == PROVIDER_NAKORDONI and CONF_PROVIDER_MODES not in user_input:
                    return self.async_show_form(step_id="nakordoni_privacy", data_schema=vol.Schema({}))
                if legacy_mode == PROVIDER_AUTO and CONF_PROVIDER_MODES not in user_input:
                    return self.async_show_form(step_id="auto_privacy", data_schema=vol.Schema({}))
                if PROVIDER_PETROMAP in provider_modes or PROVIDER_NAKORDONI in provider_modes:
                    return self.async_show_form(step_id="provider_privacy", data_schema=vol.Schema({}))
                return self.async_show_form(step_id="provider_credentials", data_schema=_credential_schema(provider_modes))
        defaults = {CONF_RADIUS: DEFAULT_RADIUS, CONF_FUEL_TYPE: DEFAULT_FUEL_TYPE, CONF_FUEL_TYPES: [DEFAULT_FUEL_TYPE], CONF_STATION_COUNT: DEFAULT_STATION_COUNT,
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL, CONF_MOVEMENT_UPDATES: DEFAULT_MOVEMENT_UPDATES,
                    CONF_MOVEMENT_THRESHOLD: DEFAULT_MOVEMENT_THRESHOLD, CONF_COOLDOWN: DEFAULT_COOLDOWN}
        return self.async_show_form(
            step_id="user", data_schema=_schema(defaults, False, True), errors=errors
        )

    async def async_step_provider_privacy(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="provider_privacy", data_schema=vol.Schema({}))
        modes = _normalize_provider_modes(self._pending_user_input.get(CONF_PROVIDER_MODES))
        return self.async_show_form(
            step_id="provider_credentials", data_schema=_credential_schema(modes)
        )

    async def async_step_provider_credentials(self, user_input=None):
        if user_input is None:
            modes = _normalize_provider_modes(self._pending_user_input.get(CONF_PROVIDER_MODES))
            return self.async_show_form(
                step_id="provider_credentials", data_schema=_credential_schema(modes)
            )
        return await self._async_create_user_entry({**self._pending_user_input, **user_input})

    async def async_step_petromap_privacy(self, user_input=None):
        """Show the Petromap data-transfer disclosure before validation."""

        if user_input is None:
            return self.async_show_form(
                step_id="petromap_privacy", data_schema=vol.Schema({})
            )
        return self.async_show_form(
            step_id="petromap_credentials",
            data_schema=_credential_schema([PROVIDER_PETROMAP]),
        )

    async def async_step_auto_privacy(self, user_input=None):
        """Show the Auto/Petromap data-transfer disclosure before validation."""

        if user_input is None:
            return self.async_show_form(step_id="auto_privacy", data_schema=vol.Schema({}))
        return self.async_show_form(
            step_id="auto_credentials",
            data_schema=_credential_schema([PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP]),
        )

    async def async_step_nakordoni_privacy(self, user_input=None):
        """Show the Nakordoni location-transfer disclosure before credentials."""

        if user_input is None:
            return self.async_show_form(step_id="nakordoni_privacy", data_schema=vol.Schema({}))
        return self.async_show_form(
            step_id="nakordoni_credentials",
            data_schema=_credential_schema([PROVIDER_NAKORDONI]),
        )

    async def async_step_tankerkoenig_credentials(self, user_input=None):
        """Collect the explicit Tankerkönig credential without validation."""

        if user_input is None:
            return self.async_show_form(
                step_id="tankerkoenig_credentials",
                data_schema=_credential_schema([PROVIDER_TANKERKOENIG]),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_petromap_credentials(self, user_input=None):
        """Collect the explicit Petromap credential without a setup request."""

        if user_input is None:
            return self.async_show_form(
                step_id="petromap_credentials",
                data_schema=_credential_schema([PROVIDER_PETROMAP]),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_auto_credentials(self, user_input=None):
        """Collect both provider credentials without a setup request."""

        if user_input is None:
            return self.async_show_form(
                step_id="auto_credentials",
                data_schema=_credential_schema([PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP]),
            )
        return await self._async_create_user_entry(
            {**self._pending_user_input, **user_input}
        )

    async def async_step_nakordoni_credentials(self, user_input=None):
        """Collect the Nakordoni credential without a setup request."""

        if user_input is None:
            return self.async_show_form(
                step_id="nakordoni_credentials",
                data_schema=_credential_schema([PROVIDER_NAKORDONI]),
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
            raw_provider_modes = user_input.get(CONF_PROVIDER_MODES)
            if isinstance(raw_provider_modes, (list, tuple, set, frozenset)) and not any(
                provider in PROVIDER_CHOICES for provider in raw_provider_modes
            ):
                return self.async_show_form(
                    step_id="init",
                    data_schema=_schema({**self.config_entry.data, **self.config_entry.options}, False, True),
                    errors={CONF_PROVIDER_MODES: "provider_required"},
                )
            self._pending_options = _normalize_sorting_input(user_input)
            # HA submits the optional checkbox as False from the native form.
            # Keeping an omitted key on the legacy path preserves callers that
            # used the pre-beta.11 flow contract.
            manage_credentials = bool(user_input.get(CONF_MANAGE_CREDENTIALS, False))
            direct_save = CONF_MANAGE_CREDENTIALS in user_input and not manage_credentials
            legacy_ui = CONF_PROVIDER_MODES not in user_input
            target_modes = _normalize_provider_modes(
                self._pending_options.get(CONF_PROVIDER_MODES),
                self.config_entry.data.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG),
            )
            if direct_save:
                return await self._async_save_general_options()
            if PROVIDER_PETROMAP in target_modes and not self.config_entry.data.get(
                CONF_PETROMAP_PRIVACY_ACCEPTED, False
            ):
                step_id = "options_petromap_privacy" if target_modes == [PROVIDER_PETROMAP] or (legacy_ui and _effective_provider_mode(target_modes) == PROVIDER_AUTO) else "options_provider_privacy"
                return self.async_show_form(step_id=step_id, data_schema=vol.Schema({}))
            if PROVIDER_NAKORDONI in target_modes and not self.config_entry.data.get(
                CONF_NAKORDONI_PRIVACY_ACCEPTED, False
            ):
                step_id = "options_nakordoni_privacy" if target_modes == [PROVIDER_NAKORDONI] else "options_provider_privacy"
                return self.async_show_form(step_id=step_id, data_schema=vol.Schema({}))
            if legacy_ui:
                return await self._async_options_credentials({})
            return await self._show_provider_credentials()
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                {**self.config_entry.data, **self.config_entry.options},
                False,
                True,
                True,
            ),
            description_placeholders=_credential_status_placeholders(
                {**self.config_entry.data, **self.config_entry.options}, self.hass, self.config_entry
            ),
        )

    async def _async_save_general_options(self):
        """Save general settings without entering credential management."""

        pending = {
            key: value for key, value in getattr(self, "_pending_options", {}).items()
            if key not in {CONF_MANAGE_CREDENTIALS, CONF_PROVIDER_MODE, CONF_PROVIDER_MODES}
        }
        selected_fuels = _normalize_fuel_types(pending.get(CONF_FUEL_TYPES, pending.get(CONF_FUEL_TYPE)))
        provider_modes = _normalize_provider_modes(
            getattr(self, "_pending_options", {}).get(CONF_PROVIDER_MODES),
            self.config_entry.data.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG),
        )
        provider_mode = _effective_provider_mode(provider_modes)
        pending[CONF_FUEL_TYPE] = _stored_fuel_value(selected_fuels)
        pending[CONF_FUEL_TYPES] = selected_fuels
        pending[CONF_PROVIDER_MODE] = provider_mode
        pending[CONF_PROVIDER_MODES] = provider_modes
        current_data = dict(self.config_entry.data)
        current_data[CONF_PROVIDER_MODE] = provider_mode
        current_data[CONF_PROVIDER_MODES] = provider_modes
        self.hass.config_entries.async_update_entry(
            self.config_entry, data=current_data, options=pending
        )
        return self.async_create_entry(title="", data=pending)

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

    async def async_step_options_provider_privacy(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="options_provider_privacy", data_schema=vol.Schema({}))
        self._petromap_privacy_accepted = PROVIDER_PETROMAP in _normalize_provider_modes(
            getattr(self, "_pending_options", {}).get(CONF_PROVIDER_MODES)
        )
        self._nakordoni_privacy_accepted = PROVIDER_NAKORDONI in _normalize_provider_modes(
            getattr(self, "_pending_options", {}).get(CONF_PROVIDER_MODES)
        )
        return await self._show_provider_credentials()

    async def _show_provider_credentials(self):
        pending = getattr(self, "_pending_options", {})
        modes = _normalize_provider_modes(
            pending.get(CONF_PROVIDER_MODES),
            self.config_entry.data.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG),
        )
        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
                step_id="provider_credentials",
                data_schema=_options_credential_schema(list(PROVIDER_CHOICES), current),
            description_placeholders=_credential_status_placeholders(current, self.hass, self.config_entry),
        )

    async def async_step_provider_credentials(self, user_input=None):
        """Replace or explicitly remove credentials without exposing them."""

        return await self._async_options_credentials(user_input or {})

    async def _async_options_credentials(self, credentials: dict[str, Any]):
        pending = getattr(self, "_pending_options", {})
        current_data = dict(self.config_entry.data)
        current_mode = current_data.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
        target_modes = _normalize_provider_modes(pending.get(CONF_PROVIDER_MODES), current_mode)
        target_mode = _effective_provider_mode(target_modes)

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

        source_keys = {
            CONF_TANKERKOENIG_API_KEY: source_tankerkoenig_key,
            CONF_PETROMAP_API_KEY: source_petromap_key,
            CONF_NAKORDONI_API_KEY: source_nakordoni_key,
        }
        updated_keys: dict[str, str] = dict(source_keys)
        changed_providers: set[str] = set()
        missing: set[str] = set()
        for provider in PROVIDER_CHOICES:
            key = _provider_key(provider)
            remove = credentials.get(f"remove_{key}", False)
            replacement = str(
                credentials.get(key)
                or (
                    credentials.get(CONF_API_KEY, "")
                    if len(target_modes) == 1 and provider == target_modes[0]
                    else ""
                )
            ).strip()
            if remove and replacement:
                return self.async_show_form(
                    step_id="provider_credentials",
                    data_schema=_options_credential_schema(list(PROVIDER_CHOICES), current_data),
                    errors={key: "credential_conflict"},
                    description_placeholders=_credential_status_placeholders(current_data, self.hass, self.config_entry),
                )
            if remove:
                updated_keys.pop(key, None)
                changed_providers.add(provider)
                continue
            if replacement:
                changed_providers.add(provider)
            updated_keys[key] = replacement or source_keys[key]
            if provider in target_modes and not updated_keys[key]:
                missing.add(key)

        if missing:
            return self.async_show_form(
                step_id="provider_credentials",
                data_schema=_options_credential_schema(list(PROVIDER_CHOICES), current_data),
                errors={key: "api_key_required" for key in missing},
                description_placeholders=_credential_status_placeholders(current_data, self.hass, self.config_entry),
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
                CONF_MANAGE_CREDENTIALS,
            }
        }
        new_data[CONF_PROVIDER_MODE] = target_mode
        new_data[CONF_PROVIDER_MODES] = target_modes
        new_data.update({key: value for key, value in updated_keys.items() if value})
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
                CONF_PROVIDER_MODES,
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
        options[CONF_PROVIDER_MODE] = target_mode
        options[CONF_PROVIDER_MODES] = target_modes
        # Update data and options together.  The OptionsFlowManager applies the
        # returned options mapping after this step; passing the same mapping here
        # makes the entry update atomic and prevents the update listener from
        # reloading a coordinator with a half-applied configuration.
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=new_data,
            options=options,
        )
        await _reset_provider_status(self.hass, self.config_entry.entry_id, changed_providers, new_data)
        return self.async_create_entry(title="", data=options)
