"""Beta.6 market, coverage, and conservative fuel-contract regressions."""

from mobile_fuel_stations.providers.base import CountryPriceCoverage, ProviderCapabilities
from mobile_fuel_stations.providers.nakordoni import (
    NAKORDONI_FUELS,
    NakordoniMarketAccess,
    extract_market_access,
)
from mobile_fuel_stations.providers.policy import choose_auto_provider
from mobile_fuel_stations.const import PROVIDER_NAKORDONI, PROVIDER_PETROMAP


def test_market_fields_remain_separate_and_secret_free():
    access = extract_market_access({
        "access_token": "DO_NOT_EXPOSE",
        "markets_approved": ["DE", "AT"],
        "markets_granted": ["DE"],
        "markets_allowed": ["DE"],
        "markets_available": ["DE", "AT", "LU"],
        "upgrade_url": "https://example.invalid/upgrade",
    })

    assert access.status_for("DE") == "allowed"
    assert access.status_for("AT") == "not_allowed"
    assert access.as_diagnostics() == {
        "markets_approved": ["AT", "DE"],
        "markets_granted": ["DE"],
        "markets_allowed": ["DE"],
        "markets_available": ["AT", "DE", "LU"],
        "upgrade_url": "https://example.invalid/upgrade",
    }
    assert "DO_NOT_EXPOSE" not in repr(access.as_diagnostics())


def test_missing_market_metadata_is_not_auto_permission():
    access = NakordoniMarketAccess()
    assert access.permitted_markets is None
    assert access.status_for("DE") == "unknown"


def test_auto_other_country_prefers_nakordoni_then_petromap():
    nakordoni = ProviderCapabilities(
        supported_fuel_types=frozenset({"diesel"}),
        country_price_coverage={"PL": CountryPriceCoverage.PER_STATION},
    )
    decision = choose_auto_provider(
        "PL", "diesel", nakordoni_enabled=True, nakordoni_capabilities=nakordoni
    )
    assert decision.provider_mode == PROVIDER_NAKORDONI

    petromap = ProviderCapabilities(
        supported_fuel_types=frozenset({"diesel"}),
        country_price_coverage={"PL": CountryPriceCoverage.PER_STATION},
    )
    decision = choose_auto_provider(
        "PL", "diesel", petromap_enabled=True, petromap_capabilities=petromap
    )
    assert decision.provider_mode == PROVIDER_PETROMAP


def test_documented_nakordoni_fuels_are_claimed_without_aliasing_hvo100():
    assert {"diesel", "e5", "e10", "superplus", "super100", "premdiesel",
            "truckdiesel", "hvo", "lpg", "cng", "adblue", "e85", "lng"} <= NAKORDONI_FUELS
    assert "hvo100" not in NAKORDONI_FUELS
