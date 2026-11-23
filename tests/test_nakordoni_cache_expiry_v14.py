"""Regression coverage for Nakordoni price-cache expiry."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from custom_components.mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator


def station(now, *, age_days=None, provider="nakordoni", updated_days=None):
    return SimpleNamespace(
        provider=provider,
        price_confirmed_at=(now - timedelta(days=age_days)) if age_days is not None else None,
        price_updated_at=(now - timedelta(days=updated_days)) if updated_days is not None else None,
    )


def test_expiry_boundary_and_missing_timestamps():
    now = datetime.now(timezone.utc)
    expired = MobileFuelStationsCoordinator._nakordoni_price_cache_expired
    assert not expired(station(now, age_days=7), now)
    assert expired(station(now, age_days=8), now)
    assert expired(station(now), now)
    assert not expired(station(now, updated_days=7), now)
    assert expired(station(now, updated_days=9), now)
    assert not expired(station(now, provider="tankerkoenig"), now)


def test_expired_runtime_result_is_removed():
    now = datetime.now(timezone.utc)
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator._has_valid_provider_result = True
    coordinator.stations = [station(now, age_days=9)]
    coordinator._cache_provider = "nakordoni"
    coordinator.data_stale = False
    coordinator._set_station_data = lambda stations: setattr(coordinator, "stations", stations)
    assert coordinator._previous_result() is None
    assert coordinator.stations == []
    assert coordinator._has_valid_provider_result is False
    assert coordinator._cache_provider is None
    assert coordinator.data_stale is True
