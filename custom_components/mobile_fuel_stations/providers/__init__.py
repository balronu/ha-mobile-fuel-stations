"""Provider selection for Mobile Fuel Stations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aiohttp import ClientSession

from ..const import (
    CONF_API_KEY,
    CONF_PETROMAP_API_KEY,
    CONF_PROVIDER_MODE,
    CONF_TANKERKOENIG_API_KEY,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
)
from .base import (
    CountryPriceCoverage,
    FuelStationProvider,
    ProviderCapabilities,
    ProviderConfigurationError,
    ProviderDisabledError,
    UnknownProviderError,
)
from .petromap import PETROMAP_CAPABILITIES, PetromapProvider
from .tankerkoenig import TankerkoenigProvider


@dataclass(frozen=True)
class ProviderRegistration:
    """Explicit registry entry for concrete providers and strategies."""

    provider_id: str
    factory: Callable[[ClientSession, str], FuelStationProvider] | None
    enabled: bool
    capabilities: ProviderCapabilities
    is_strategy: bool = False


CONCRETE_PROVIDER_IDS = frozenset({PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP})
STRATEGY_PROVIDER_IDS = frozenset({PROVIDER_AUTO})


PROVIDER_REGISTRY: dict[str, ProviderRegistration] = {
    PROVIDER_TANKERKOENIG: ProviderRegistration(
        provider_id=PROVIDER_TANKERKOENIG,
        factory=TankerkoenigProvider,
        enabled=True,
        capabilities=ProviderCapabilities(
            supported_countries=frozenset({"DE"}),
            supported_fuel_types=frozenset({"diesel", "e5", "e10"}),
            max_radius_km=25.0,
            country_price_coverage={"DE": CountryPriceCoverage.PER_STATION},
        ),
    ),
    PROVIDER_PETROMAP: ProviderRegistration(
        provider_id=PROVIDER_PETROMAP,
        factory=PetromapProvider,
        enabled=True,
        capabilities=PETROMAP_CAPABILITIES,
    ),
    PROVIDER_AUTO: ProviderRegistration(
        provider_id=PROVIDER_AUTO,
        factory=None,
        enabled=False,
        capabilities=ProviderCapabilities(),
        is_strategy=True,
    ),
}


def create_provider(session: ClientSession, config: dict[str, object]) -> FuelStationProvider:
    """Create the active provider without exposing provider details to the coordinator."""
    mode = config.get(CONF_PROVIDER_MODE, PROVIDER_TANKERKOENIG)
    registration = PROVIDER_REGISTRY.get(str(mode))
    if registration is None:
        raise UnknownProviderError(f"Unknown provider mode: {mode}")
    if registration.is_strategy or not registration.enabled or registration.factory is None:
        raise ProviderDisabledError(f"Provider mode is disabled: {mode}")
    key_name = (
        CONF_PETROMAP_API_KEY
        if mode == PROVIDER_PETROMAP
        else CONF_TANKERKOENIG_API_KEY
    )
    api_key = config.get(key_name) or config.get(CONF_API_KEY)
    if not api_key:
        raise ProviderConfigurationError(f"Missing credential for provider: {mode}")
    return registration.factory(session, str(api_key))


__all__ = [
    "FuelStationProvider",
    "CountryPriceCoverage",
    "ProviderCapabilities",
    "ProviderConfigurationError",
    "ProviderDisabledError",
    "ProviderRegistration",
    "CONCRETE_PROVIDER_IDS",
    "STRATEGY_PROVIDER_IDS",
    "PETROMAP_CAPABILITIES",
    "PROVIDER_REGISTRY",
    "TankerkoenigProvider",
    "UnknownProviderError",
    "create_provider",
]
