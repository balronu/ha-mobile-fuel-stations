"""Provider selection for Mobile Fuel Stations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aiohttp import ClientSession

from ..const import CONF_PROVIDER_MODE, PROVIDER_AUTO, PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG
from .base import (
    FuelStationProvider,
    ProviderCapabilities,
    ProviderConfigurationError,
    ProviderDisabledError,
    UnknownProviderError,
)
from .tankerkoenig import TankerkoenigProvider


@dataclass(frozen=True)
class ProviderRegistration:
    """Explicit registry entry; disabled entries have no factory."""

    provider_id: str
    factory: Callable[[ClientSession, str], FuelStationProvider] | None
    enabled: bool
    capabilities: ProviderCapabilities


PROVIDER_REGISTRY: dict[str, ProviderRegistration] = {
    PROVIDER_TANKERKOENIG: ProviderRegistration(
        provider_id=PROVIDER_TANKERKOENIG,
        factory=TankerkoenigProvider,
        enabled=True,
        capabilities=ProviderCapabilities(
            supported_countries=frozenset({"DE"}),
            supported_fuel_types=frozenset({"diesel", "e5", "e10"}),
            max_radius_km=25.0,
        ),
    ),
    # Deliberately no factory or concrete capabilities: Petromap is not implemented in R2B.
    PROVIDER_PETROMAP: ProviderRegistration(
        provider_id=PROVIDER_PETROMAP,
        factory=None,
        enabled=False,
        capabilities=ProviderCapabilities(),
    ),
    PROVIDER_AUTO: ProviderRegistration(
        provider_id=PROVIDER_AUTO,
        factory=None,
        enabled=False,
        capabilities=ProviderCapabilities(),
    ),
}


def create_provider(session: ClientSession, config: dict[str, object]) -> FuelStationProvider:
    """Create the active provider without exposing provider details to the coordinator."""
    mode = config.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
    registration = PROVIDER_REGISTRY.get(str(mode))
    if registration is None:
        raise UnknownProviderError(f"Unknown provider mode: {mode}")
    if not registration.enabled or registration.factory is None:
        raise ProviderDisabledError(f"Provider mode is disabled: {mode}")
    return registration.factory(session, str(config["api_key"]))


__all__ = [
    "FuelStationProvider",
    "ProviderCapabilities",
    "ProviderConfigurationError",
    "ProviderDisabledError",
    "ProviderRegistration",
    "PROVIDER_REGISTRY",
    "TankerkoenigProvider",
    "UnknownProviderError",
    "create_provider",
]
