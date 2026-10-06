"""Pure, offline provider-selection primitives for the future auto mode.

The coordinator may evaluate these primitives to prepare internal context,
but the registry still controls the active provider. This module performs no
I/O, does not resolve coordinates, and does not activate ``auto`` or Petromap.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..const import PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG
from .base import (
    CountryPriceCoverage,
    FuelFallbackBlockedError,
    FuelResolution,
    NoSuitableProviderError,
    ProviderCapabilities,
    ProviderError,
    ProviderUnavailableError,
    resolve_fuel,
)
from .petromap import PETROMAP_CAPABILITIES

# Compatibility aliases; the capability object above is the only definition.
PETROMAP_COUNTRY_COVERAGE = PETROMAP_CAPABILITIES.country_price_coverage
PETROMAP_FUEL_TYPES = PETROMAP_CAPABILITIES.supported_fuel_types
TANKERKOENIG_FUEL_TYPES = frozenset({"diesel", "e5", "e10"})
TANKERKOENIG_CAPABILITIES = ProviderCapabilities(
    supported_countries=frozenset({"DE"}),
    supported_fuel_types=TANKERKOENIG_FUEL_TYPES,
    max_radius_km=25.0,
    country_price_coverage={"DE": CountryPriceCoverage.PER_STATION},
)


def normalize_country_code(value: str | None) -> str | None:
    """Return only a normalized ISO-3166-1 alpha-2 code."""

    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized if len(normalized) == 2 and normalized.isalpha() else None


@dataclass(slots=True, frozen=True)
class AutoProviderDecision:
    """Machine-readable result of a future auto-provider decision."""

    provider_mode: str | None
    country_code: str | None
    coverage: CountryPriceCoverage
    reason: str
    fuel_resolution: FuelResolution | None = None


@dataclass(slots=True, frozen=True)
class AutoRuntimeState:
    """Secret-free state contract for a future Auto coordinator runtime."""

    configured_provider_mode: str
    effective_provider: str | None
    raw_country: str | None
    confirmed_country: str | None
    coverage: CountryPriceCoverage
    fuel_resolution: FuelResolution | None
    reason: str


def validate_direct_fuel_runtime(decision: AutoProviderDecision) -> AutoProviderDecision:
    """Reject Auto outcomes that cannot make one direct provider request."""

    if decision.provider_mode is None:
        raise NoSuitableProviderError(decision.reason)
    if decision.fuel_resolution and decision.fuel_resolution.fallback_used:
        raise FuelFallbackBlockedError(
            decision.fuel_resolution.fallback_reason or "fallback_required"
        )
    return decision


def is_expected_auto_unavailable(error: ProviderError) -> bool:
    """Identify policy states that must not be treated as transport failures."""

    return isinstance(error, (NoSuitableProviderError, FuelFallbackBlockedError))


def _coverage_for(
    capabilities: ProviderCapabilities | None,
    country_code: str,
) -> CountryPriceCoverage:
    if capabilities is None:
        return CountryPriceCoverage.UNKNOWN
    coverage = capabilities.country_price_coverage or {}
    return coverage.get(country_code, CountryPriceCoverage.UNSUPPORTED)


def choose_auto_provider(
    country_code: str | None,
    fuel_type: str,
    *,
    tankerkoenig_enabled: bool = True,
    tankerkoenig_capabilities: ProviderCapabilities | None = None,
    petromap_enabled: bool = False,
    petromap_capabilities: ProviderCapabilities | None = None,
) -> AutoProviderDecision:
    """Choose a provider without I/O, HA state, geocoding, or fallback calls.

    Tankerkönig is deliberately preferred for Germany.  Petromap can only be
    returned when an explicitly supplied hypothetical capability says that
    per-station prices and the requested fuel are available.
    """

    normalized = normalize_country_code(country_code)
    if normalized is None:
        return AutoProviderDecision(None, None, CountryPriceCoverage.UNKNOWN, "unsupported_country")

    tanker_capabilities = tankerkoenig_capabilities or TANKERKOENIG_CAPABILITIES
    tanker_fuel = resolve_fuel(fuel_type, tanker_capabilities)
    tanker_coverage = _coverage_for(tanker_capabilities, normalized)
    if (
        normalized == "DE"
        and tankerkoenig_enabled
        and tanker_coverage == CountryPriceCoverage.PER_STATION
        and tanker_fuel.effective_fuel is not None
    ):
        return AutoProviderDecision(
            PROVIDER_TANKERKOENIG,
            normalized,
            tanker_coverage,
            "preferred_provider",
            tanker_fuel,
        )

    petromap_capabilities = petromap_capabilities or PETROMAP_CAPABILITIES
    petromap_coverage = _coverage_for(petromap_capabilities, normalized)
    if petromap_coverage != CountryPriceCoverage.PER_STATION:
        reason = {
            CountryPriceCoverage.NATIONAL_ONLY: "national_prices_only",
            CountryPriceCoverage.NO_PRICES: "no_station_prices",
            CountryPriceCoverage.UNSUPPORTED: "unsupported_country",
            CountryPriceCoverage.UNKNOWN: "unknown_coverage",
        }.get(petromap_coverage, "unsupported_country")
        return AutoProviderDecision(None, normalized, petromap_coverage, reason)
    if not petromap_enabled:
        return AutoProviderDecision(None, normalized, petromap_coverage, "provider_disabled")
    supported_fuels = petromap_capabilities.supported_fuel_types or frozenset()
    petromap_fuel = resolve_fuel(
        fuel_type,
        ProviderCapabilities(supported_fuel_types=supported_fuels),
    )
    if petromap_fuel.effective_fuel is None:
        return AutoProviderDecision(
            None,
            normalized,
            petromap_coverage,
            "unsupported_fuel",
            petromap_fuel,
        )
    return AutoProviderDecision(
        PROVIDER_PETROMAP,
        normalized,
        petromap_coverage,
        "provider_available",
        petromap_fuel,
    )


class CountryHysteresis:
    """Small in-memory debounce for future country resolver results."""

    def __init__(self, confirmations: int = 3) -> None:
        if confirmations < 1:
            raise ValueError("confirmations must be positive")
        self.confirmations = confirmations
        self.confirmed_country: str | None = None
        self._candidate: str | None = None
        self._candidate_count = 0

    def observe(self, country_code: str | None) -> str | None:
        """Return the currently confirmed country after deterministic debounce."""

        normalized = normalize_country_code(country_code)
        if normalized is None:
            self._candidate = None
            self._candidate_count = 0
            return self.confirmed_country
        if self.confirmed_country is None:
            self.confirmed_country = normalized
            return self.confirmed_country
        if normalized == self.confirmed_country:
            self._candidate = None
            self._candidate_count = 0
            return self.confirmed_country
        if normalized != self._candidate:
            self._candidate = normalized
            self._candidate_count = 1
        else:
            self._candidate_count += 1
        if self._candidate_count >= self.confirmations:
            self.confirmed_country = normalized
            self._candidate = None
            self._candidate_count = 0
        return self.confirmed_country


__all__ = [
    "AutoProviderDecision",
    "AutoRuntimeState",
    "CountryHysteresis",
    "FuelFallbackBlockedError",
    "FuelResolution",
    "NoSuitableProviderError",
    "PETROMAP_CAPABILITIES",
    "PETROMAP_COUNTRY_COVERAGE",
    "TANKERKOENIG_CAPABILITIES",
    "choose_auto_provider",
    "normalize_country_code",
    "resolve_fuel",
    "is_expected_auto_unavailable",
    "validate_direct_fuel_runtime",
]
