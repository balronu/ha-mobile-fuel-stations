import pytest

from mobile_fuel_stations.const import PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, create_provider
from mobile_fuel_stations.providers.base import (
    CountryPriceCoverage,
    ProviderCapabilities,
    ProviderDisabledError,
    FuelFallbackBlockedError,
    NoSuitableProviderError,
    ProviderReauthContext,
    ProviderUnavailableError,
    resolve_fuel,
)
from mobile_fuel_stations.providers.policy import (
    CountryHysteresis,
    choose_auto_provider,
    normalize_country_code,
    is_expected_auto_unavailable,
    validate_direct_fuel_runtime,
)
from mobile_fuel_stations.providers.petromap import PETROMAP_CAPABILITIES


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


def test_auto_routes_german_lpg_to_petromap_when_tankerkoenig_lacks_lpg():
    decision = choose_auto_provider("DE", "lpg", petromap_enabled=True)
    assert decision.provider_mode == PROVIDER_PETROMAP
    assert decision.fuel_resolution is not None
    assert decision.fuel_resolution.effective_fuel == "lpg"
    assert decision.fuel_resolution.fallback_used is False


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
    assert PROVIDER_REGISTRY["auto"].is_strategy is True
    try:
        create_provider(object(), {"api_key": "secret", "provider_mode": "auto"})
    except ProviderDisabledError:
        pass
    else:
        raise AssertionError("auto must remain disabled")


def test_registry_and_policy_share_petromap_capabilities():
    assert PROVIDER_REGISTRY[PROVIDER_PETROMAP].capabilities is PETROMAP_CAPABILITIES
    assert PETROMAP_CAPABILITIES.supported_countries == frozenset({"DE", "AT"})
    assert PETROMAP_CAPABILITIES.supported_fuel_types == frozenset({"diesel", "e5", "lpg"})
    assert PETROMAP_CAPABILITIES.max_radius_km == 25.0

    for fuel in ("diesel", "e5", "lpg"):
        decision = choose_auto_provider("AT", fuel, petromap_enabled=True)
        assert decision.provider_mode == PROVIDER_PETROMAP
        assert decision.fuel_resolution is not None
        assert decision.fuel_resolution.effective_fuel == fuel


def test_hvo100_is_not_selectable_without_a_verified_provider_contract():
    assert "hvo100" not in PETROMAP_CAPABILITIES.supported_fuel_types
    assert "hvo100" not in TANKERKOENIG.supported_fuel_types
    assert resolve_fuel("hvo100", PETROMAP_CAPABILITIES).effective_fuel is None


def test_c2b_outcomes_are_pre_network_and_distinct():
    unsupported = choose_auto_provider("RS", "diesel", petromap_enabled=True)
    with pytest.raises(NoSuitableProviderError):
        validate_direct_fuel_runtime(unsupported)

    fallback = choose_auto_provider("AT", "e10", petromap_enabled=True)
    assert validate_direct_fuel_runtime(fallback) == fallback
    assert is_expected_auto_unavailable(NoSuitableProviderError("unsupported_country"))
    assert is_expected_auto_unavailable(FuelFallbackBlockedError("fallback_required"))
    assert not is_expected_auto_unavailable(ProviderUnavailableError("503"))


def test_provider_reauth_context_is_secret_free_and_serializable():
    context = ProviderReauthContext(PROVIDER_PETROMAP)
    assert context.as_dict() == {"provider_mode": PROVIDER_PETROMAP}
    assert ProviderReauthContext.from_dict(context.as_dict()) == context
    assert "secret" not in repr(context).lower()
