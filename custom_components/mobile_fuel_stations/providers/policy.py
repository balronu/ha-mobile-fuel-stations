"""Pure, offline provider-selection policy for a future auto mode.

This module is intentionally not imported by the coordinator or registry.
R2C-3 only prepares deterministic policy primitives; it does not resolve
coordinates to countries and does not activate ``auto`` or Petromap.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..const import PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG
from .base import CountryPriceCoverage, ProviderCapabilities

PETROMAP_COUNTRY_COVERAGE: dict[str, CountryPriceCoverage] = {
    "DE": CountryPriceCoverage.PER_STATION,
    "AT": CountryPriceCoverage.PER_STATION,
    "BG": CountryPriceCoverage.NATIONAL_ONLY,
    "PL": CountryPriceCoverage.NATIONAL_ONLY,
    "SK": CountryPriceCoverage.NATIONAL_ONLY,
    "ME": CountryPriceCoverage.NO_PRICES,
    "RS": CountryPriceCoverage.NO_PRICES,
}

PETROMAP_FUEL_TYPES = frozenset({"diesel", "e5"})
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
    tanker_coverage = _coverage_for(tanker_capabilities, normalized)
    if (
        normalized == "DE"
        and tankerkoenig_enabled
        and tanker_coverage == CountryPriceCoverage.PER_STATION
        and fuel_type in (tanker_capabilities.supported_fuel_types or frozenset())
    ):
        return AutoProviderDecision(PROVIDER_TANKERKOENIG, normalized, tanker_coverage, "preferred_provider")

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
    supported_fuels = petromap_capabilities.supported_fuel_types if petromap_capabilities else PETROMAP_FUEL_TYPES
    if fuel_type not in supported_fuels:
        return AutoProviderDecision(None, normalized, petromap_coverage, "unsupported_fuel")
    return AutoProviderDecision(PROVIDER_PETROMAP, normalized, petromap_coverage, "provider_available")


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
    "CountryHysteresis",
    "PETROMAP_COUNTRY_COVERAGE",
    "TANKERKOENIG_CAPABILITIES",
    "choose_auto_provider",
    "normalize_country_code",
]
