import json
import asyncio

import pytest

from mobile_fuel_stations import coordinator as coordinator_module
from mobile_fuel_stations.const import (
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    PROVIDER_TANKERKOENIG,
    PROVIDER_PETROMAP,
)
from mobile_fuel_stations.coordinator import CountryAutoContext, MobileFuelStationsCoordinator
from mobile_fuel_stations.providers.base import CountryPriceCoverage


def _context(results: list[object]) -> CountryAutoContext:
    values = iter(results)

    def resolver(_lat: float, _lon: float) -> str | None:
        result = next(values)
        if isinstance(result, BaseException):
            raise result
        return result

    return CountryAutoContext("diesel", resolver=resolver)


def test_initial_gps_resolution_confirms_de_and_prepares_tankerkoenig():
    context = _context(["DE"])

    decision = context.observe_position((49.2402, 6.9969))

    assert context.raw_country == "DE"
    assert context.confirmed_country == "DE"
    assert decision.provider_mode == PROVIDER_TANKERKOENIG
    assert decision.country_code == "DE"
    assert decision.reason == "preferred_provider"


def test_auto_policy_never_uses_provider_outside_active_allowlist():
    context = CountryAutoContext(
        "diesel", resolver=lambda _lat, _lon: "DE", allowed_providers={PROVIDER_PETROMAP}
    )

    decision = context.observe_position((49.2402, 6.9969))

    assert decision.provider_mode == PROVIDER_PETROMAP
    assert decision.country_code == "DE"


def test_country_change_requires_three_confirmations():
    context = _context(["DE", "FR", "FR", "FR"])

    assert context.observe_position((1, 1)).country_code == "DE"
    assert context.observe_position((1, 1)).country_code == "DE"
    assert context.observe_position((1, 1)).country_code == "DE"
    assert context.observe_position((1, 1)).country_code == "FR"
    assert context.confirmed_country == "FR"


def test_candidate_country_resets_when_observation_jumps_back():
    context = _context(["DE", "FR", "FR", "DE", "FR", "FR", "FR"])

    decisions = [context.observe_position((1, 1)) for _ in range(7)]

    assert [decision.country_code for decision in decisions] == ["DE", "DE", "DE", "DE", "DE", "DE", "FR"]


def test_none_keeps_confirmed_country_and_resets_candidate():
    context = _context(["DE", "FR", "FR", None, "FR", "FR", "FR"])

    decisions = [context.observe_position((1, 1)) for _ in range(7)]

    assert [decision.country_code for decision in decisions] == ["DE", "DE", "DE", "DE", "DE", "DE", "FR"]
    assert context.raw_country == "FR"
    assert context.confirmed_country == "FR"


def test_at_prepares_petromap_decision_without_switching_runtime_provider():
    context = _context(["AT"])

    decision = context.observe_position((48.2082, 16.3738))

    assert context.confirmed_country == "AT"
    assert decision.provider_mode == PROVIDER_PETROMAP
    assert decision.coverage == CountryPriceCoverage.PER_STATION
    assert decision.reason == "provider_available"


def test_policy_context_is_pure_and_does_not_make_requests():
    calls = []

    def resolver(latitude: float, longitude: float) -> str:
        calls.append((latitude, longitude))
        return "DE"

    context = CountryAutoContext("diesel", resolver=resolver)
    context.observe_position((50.0, 8.0))

    assert calls == [(50.0, 8.0)]


@pytest.mark.parametrize(
    "failure",
    [OSError("dataset unavailable"), json.JSONDecodeError("invalid", "{", 0), KeyError("countries")],
)
def test_expected_dataset_failures_fail_open_and_keep_confirmed_country(failure):
    context = _context(["DE", failure])
    context.observe_position((1, 1))

    decision = context.observe_position((1, 1))

    assert context.raw_country is None
    assert context.confirmed_country == "DE"
    assert decision.provider_mode == PROVIDER_TANKERKOENIG


def test_expected_dataset_failure_resets_country_candidate():
    context = _context(["DE", "FR", "FR", OSError("dataset unavailable"), "FR", "FR", "FR"])

    decisions = [context.observe_position((1, 1)) for _ in range(7)]

    assert [decision.country_code for decision in decisions] == ["DE", "DE", "DE", "DE", "DE", "DE", "FR"]


def test_first_expected_dataset_failure_keeps_context_empty_then_recovers():
    context = _context([OSError("dataset unavailable"), "DE"])

    failed = context.observe_position((1, 1))
    recovered = context.observe_position((1, 1))

    assert context.raw_country == "DE"
    assert failed.country_code is None
    assert failed.provider_mode is None
    assert recovered.country_code == "DE"
    assert recovered.provider_mode == PROVIDER_TANKERKOENIG


def test_unclassified_programming_error_is_not_swallowed():
    context = _context([RuntimeError("programming bug")])

    with pytest.raises(RuntimeError, match="programming bug"):
        context.observe_position((1, 1))


@pytest.mark.parametrize(
    "failure",
    [OSError("dataset unavailable"), json.JSONDecodeError("invalid", "{", 0), KeyError("countries")],
)
def test_coordinator_fail_open_keeps_exactly_one_existing_provider_request(monkeypatch, failure):
    class FakeProvider:
        def __init__(self):
            self.calls = 0

        async def async_search(self, _query):
            self.calls += 1
            return []

    class FakeStore:
        async def async_save(self, _data):
            return None

    provider = FakeProvider()
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.hass = object()
    coordinator.options = {
        CONF_LOCATION_ENTITY: "device_tracker.car",
        CONF_RADIUS: 25,
        CONF_FUEL_TYPE: "diesel",
        CONF_STATION_COUNT: 3,
    }
    coordinator.client = provider
    coordinator.stations = []
    coordinator.nearest_station = None
    coordinator.cheapest_station = None
    coordinator.last_successful_update = None
    coordinator.reference_position = None
    coordinator.last_request = None
    coordinator._store = FakeStore()
    coordinator.country_auto_context = _context(["DE", failure])
    coordinator.country_auto_context.observe_position((49.0, 7.0))
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda _hass, _entity: (49.0, 7.0))

    asyncio.run(coordinator._async_update_data())

    assert provider.calls == 1
    assert coordinator.country_auto_context.raw_country is None
    assert coordinator.country_auto_context.confirmed_country == "DE"
