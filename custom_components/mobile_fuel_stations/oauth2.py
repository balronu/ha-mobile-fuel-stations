"""Nakordoni OAuth2-PKCE implementation using Home Assistant helpers."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    LocalOAuth2ImplementationWithPkce,
    MY_AUTH_CALLBACK_PATH,
    async_get_config_entry_implementation,
    async_register_implementation,
)

from .const import (
    DOMAIN,
    NAKORDONI_OAUTH_AUTHORIZE_URL,
    NAKORDONI_OAUTH_CLIENT_ID,
    NAKORDONI_OAUTH_IMPLEMENTATION,
    NAKORDONI_OAUTH_TOKEN_URL,
)


class NakordoniOAuth2Implementation(LocalOAuth2ImplementationWithPkce):
    """PKCE implementation pinned to Nakordoni's sole registered redirect."""

    @property
    def redirect_uri(self) -> str:
        """Return the only redirect URI registered for the public client."""

        return MY_AUTH_CALLBACK_PATH


def create_implementation(hass: HomeAssistant) -> NakordoniOAuth2Implementation:
    """Create the public Nakordoni client; no client secret is used."""

    implementation = NakordoniOAuth2Implementation(
        hass,
        NAKORDONI_OAUTH_IMPLEMENTATION,
        NAKORDONI_OAUTH_CLIENT_ID,
        NAKORDONI_OAUTH_AUTHORIZE_URL,
        NAKORDONI_OAUTH_TOKEN_URL,
        client_secret="",
    )
    return implementation


def async_register(hass: HomeAssistant) -> None:
    """Register the fixed public client for the integration's OAuth flow."""

    async_register_implementation(hass, DOMAIN, create_implementation(hass))


__all__ = [
    "async_get_config_entry_implementation",
    "async_register",
    "create_implementation",
]
