"""Provider selection for Mobile Fuel Stations."""

from __future__ import annotations

from aiohttp import ClientSession

from ..const import CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG
from .base import ProviderConfigurationError, FuelStationProvider
from .tankerkoenig import TankerkoenigProvider


def create_provider(session: ClientSession, config: dict[str, object]) -> FuelStationProvider:
    """Create the active provider without exposing provider details to the coordinator."""
    mode = config.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
    if mode != PROVIDER_TANKERKOENIG:
        raise ProviderConfigurationError(f"Unsupported provider mode: {mode}")
    return TankerkoenigProvider(session, str(config["api_key"]))


__all__ = ["FuelStationProvider", "ProviderConfigurationError", "TankerkoenigProvider", "create_provider"]
