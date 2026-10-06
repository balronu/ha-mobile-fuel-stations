from mobile_fuel_stations.const import PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, create_provider
from mobile_fuel_stations.providers.base import (
    CountryPriceCoverage,
    ProviderCapabilities,
    ProviderDisabledError,
    resolve_fuel,
)
from mobile_fuel_stations.providers.policy import CountryHysteresis, choose_auto_provider, normalize_country_code


PETROMAP_HYPOTHETICAL = ProviderCapabilities(
    supported_countries=frozenset({"DE", "AT"}),
    supported_fuel_types=frozenset({"diesel", "e5"}),
    country_price_coverage={
        "DE": CountryPriceCoverage.PER_STATION,
        "AT": CountryPriceCoverage.PER_STATION,
        "PL": CountryPriceCoverage.NATIONAL_ONLY,
        "BG": CountryPriceCoverage.NATIONAL_ONLY,
        "SK": CountryPriceCoverage.NATIONAL_ONLY,
        "ME": CountryPriceCoverage.NO_PRICES,
        "RS": CountryPriceCoverage.NO_PRICES,
    },
)

TANKERKOENIG = ProviderCapabilities(
    supported_countries=frozenset({"DE"}),
    supported_fuel_types=frozenset({"diesel", "e5", "e10"}),
    country_price_coverage={"DE": CountryPriceCoverage.PER_STATION},
)


def test_country_normalization_is_strict_iso_alpha2():
    assert normalize_country_code("de") == "DE"
    assert normalize_country_code(" De ") == "DE"
    assert normalize_country_code("AT") == "AT"
    assert normalize_country_code(None) is None
    assert normalize_country_code("Germany") is None
    assert normalize_country_code("D1") is None


def test_fuel_resolution_preserves_supported_fuels_without_fallback():
    capabilities = ProviderCapabilities(supported_fuel_types=frozenset({"diesel", "e5", "e10"}))
    for fuel in ("diesel", "e5", "e10"):
        resolution = resolve_fuel(fuel, capabilities)
        assert resolution.requested_fuel == fuel
        assert resolution.effective_fuel == fuel
        assert resolution.fallback_used is False
        assert resolution.fallback_reason is None


def test_fuel_resolution_allows_only_e10_to_e5_fallback():
    capabilities = ProviderCapabilities(supported_fuel_types=frozenset({"diesel", "e5"}))

    resolution = resolve_fuel("e10", capabilities)
    assert resolution.effective_fuel == "e5"
    assert resolution.fallback_used is True
    assert resolution.fallback_reason == "provider_unsupported"
    assert resolve_fuel("e5", ProviderCapabilities(supported_fuel_types=frozenset({"e10"}))).effective_fuel is None
    assert resolve_fuel("diesel", ProviderCapabilities(supported_fuel_types=frozenset({"e5", "e10"}))).effective_fuel is None


def test_fuel_resolution_returns_unsupported_without_cross_fuel_fallback():
    resolution = resolve_fuel("e10", ProviderCapabilities(supported_fuel_types=frozenset({"diesel"})))
    assert resolution.effective_fuel is None
    assert resolution.fallback_used is False
    assert resolution.fallback_reason == "provider_unsupported"


def test_auto_prefers_tankerkoenig_for_all_supported_german_fuels():
    for fuel in ("diesel", "e5", "e10"):
        decision = choose_auto_provider("DE", fuel, tankerkoenig_capabilities=TANKERKOENIG)
        assert decision.provider_mode == PROVIDER_TANKERKOENIG
        assert decision.reason == "preferred_provider"
        assert decision.fuel_resolution is not None
        assert decision.fuel_resolution.effective_fuel == fuel


def test_auto_uses_e10_for_tankerkoenig_even_when_fallback_exists_elsewhere():
    decision = choose_auto_provider("DE", "e10", tankerkoenig_capabilities=TANKERKOENIG)
    assert decision.provider_mode == PROVIDER_TANKERKOENIG
    assert decision.fuel_resolution is not None
    assert decision.fuel_resolution.effective_fuel == "e10"
    assert decision.fuel_resolution.fallback_used is False


def test_auto_has_tankerkoenig_as_the_default_german_capability():
    assert choose_auto_provider("DE", "diesel").provider_mode == PROVIDER_TANKERKOENIG


def test_auto_petromap_disabled_is_never_selected():
    decision = choose_auto_provider("AT", "diesel", petromap_capabilities=PETROMAP_HYPOTHETICAL)
    assert decision.provider_mode is None
    assert decision.reason == "provider_disabled"


def test_auto_hypothetical_petromap_selection_is_capability_and_fuel_aware():
    assert choose_auto_provider(
        "AT", "diesel", petromap_enabled=True, petromap_capabilities=PETROMAP_HYPOTHETICAL
    ).provider_mode == PROVIDER_PETROMAP
    e10_decision = choose_auto_provider(
        "AT", "e10", petromap_enabled=True, petromap_capabilities=PETROMAP_HYPOTHETICAL
    )
    assert e10_decision.provider_mode == PROVIDER_PETROMAP
    assert e10_decision.fuel_resolution is not None
    assert e10_decision.fuel_resolution.effective_fuel == "e5"
    assert e10_decision.fuel_resolution.fallback_used is True
    assert e10_decision.fuel_resolution.fallback_reason == "provider_unsupported"


def test_auto_rejects_national_only_and_no_price_coverage():
    for country in ("PL", "BG", "SK"):
        decision = choose_auto_provider(
            country, "diesel", petromap_enabled=True, petromap_capabilities=PETROMAP_HYPOTHETICAL
        )
        assert decision.coverage == CountryPriceCoverage.NATIONAL_ONLY
        assert decision.reason == "national_prices_only"
    for country in ("ME", "RS"):
        decision = choose_auto_provider(
            country, "diesel", petromap_enabled=True, petromap_capabilities=PETROMAP_HYPOTHETICAL
        )
        assert decision.coverage == CountryPriceCoverage.NO_PRICES
        assert decision.reason == "no_station_prices"


def test_auto_unknown_country_is_unsupported():
    decision = choose_auto_provider("FR", "diesel", petromap_enabled=True, petromap_capabilities=PETROMAP_HYPOTHETICAL)
    assert decision.provider_mode is None
    assert decision.reason == "unsupported_country"


def test_country_hysteresis_requires_three_consecutive_new_results():
    hysteresis = CountryHysteresis()
    assert hysteresis.observe("DE") == "DE"
    assert hysteresis.observe("FR") == "DE"
    assert hysteresis.observe("FR") == "DE"
    assert hysteresis.observe("FR") == "FR"


def test_country_hysteresis_resets_candidate_when_result_jumps_back():
    hysteresis = CountryHysteresis()
    hysteresis.observe("DE")
    assert hysteresis.observe("FR") == "DE"
    assert hysteresis.observe("AT") == "DE"
    assert hysteresis.observe("FR") == "DE"
    assert hysteresis.observe("FR") == "DE"
    assert hysteresis.observe("FR") == "FR"


def test_registry_enables_petromap_but_keeps_auto_disabled():
    assert PROVIDER_REGISTRY[PROVIDER_PETROMAP].enabled is True
    assert PROVIDER_REGISTRY[PROVIDER_PETROMAP].factory is not None
    assert PROVIDER_REGISTRY["auto"].enabled is False
    assert PROVIDER_REGISTRY["auto"].factory is None
    try:
        create_provider(object(), {"api_key": "secret", "provider_mode": "auto"})
    except ProviderDisabledError:
        pass
    else:
        raise AssertionError("auto must remain disabled")
