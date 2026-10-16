"""Home Assistant OAuth2 helper contract tests for Nakordoni.

These tests intentionally use the real HA helper classes.  They are not run in
the local Python 3.13 fallback environment because HA 2026.10.1 requires
Python >=3.14.2.
"""

from urllib.parse import parse_qs, urlparse

import pytest

from homeassistant.helpers import config_entry_oauth2_flow

from mobile_fuel_stations.const import (
    NAKORDONI_OAUTH_AUTHORIZE_URL,
    NAKORDONI_OAUTH_CLIENT_ID,
    NAKORDONI_OAUTH_TOKEN_URL,
)
from mobile_fuel_stations.oauth2 import create_implementation


@pytest.mark.asyncio
async def test_nakordoni_authorize_url_uses_my_redirect_and_s256(hass):
    """The registered redirect and PKCE S256 parameters are exact."""

    hass.config.components.add("my")
    implementation = create_implementation(hass)
    url = await implementation.async_generate_authorize_url("flow-id")
    query = parse_qs(urlparse(url).query)

    assert urlparse(url).scheme == "https"
    assert urlparse(url).netloc == "api.nakordoni.dev"
    assert urlparse(url).path == "/oauth/authorize"
    assert query["client_id"] == [NAKORDONI_OAUTH_CLIENT_ID]
    assert query["redirect_uri"] == ["https://my.home-assistant.io/redirect/oauth"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"] == [
        config_entry_oauth2_flow.LocalOAuth2ImplementationWithPkce.compute_code_challenge(
            implementation.code_verifier
        )
    ]
    assert implementation.token_url == NAKORDONI_OAUTH_TOKEN_URL
    assert implementation.authorize_url == NAKORDONI_OAUTH_AUTHORIZE_URL


class _TokenResponse:
    status = 200

    async def json(self):
        return {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

    def raise_for_status(self):
        return None


class _TokenSession:
    def __init__(self):
        self.data = None

    async def post(self, url, data):
        self.data = data
        return _TokenResponse()


@pytest.mark.asyncio
async def test_nakordoni_code_exchange_uses_verifier_without_client_secret(hass, monkeypatch):
    """The code exchange is public-client PKCE and never sends a secret."""

    hass.config.components.add("my")
    implementation = create_implementation(hass)
    session = _TokenSession()
    monkeypatch.setattr(
        config_entry_oauth2_flow,
        "async_get_clientsession",
        lambda _hass: session,
    )

    token = await implementation.async_resolve_external_data(
        {
            "code": "one-time-code",
            "state": {"redirect_uri": "https://my.home-assistant.io/redirect/oauth"},
        }
    )

    assert token["access_token"] == "test-access-token"
    assert session.data["client_id"] == NAKORDONI_OAUTH_CLIENT_ID
    assert session.data["code_verifier"] == implementation.code_verifier
    assert "client_secret" not in session.data
    assert session.data["redirect_uri"] == "https://my.home-assistant.io/redirect/oauth"


@pytest.mark.asyncio
async def test_nakordoni_refresh_uses_refresh_grant_without_client_secret(hass, monkeypatch):
    """HA's helper sends the public-client refresh grant as specified."""

    session = _TokenSession()
    monkeypatch.setattr(
        config_entry_oauth2_flow,
        "async_get_clientsession",
        lambda _hass: session,
    )
    implementation = create_implementation(hass)

    token = await implementation.async_refresh_token(
        {
            "access_token": "old-access-token",
            "refresh_token": "refresh-token",
            "expires_at": 0,
        }
    )

    assert token["access_token"] == "test-access-token"
    assert session.data["grant_type"] == "refresh_token"
    assert session.data["refresh_token"] == "refresh-token"
    assert "client_secret" not in session.data
