"""Regression tests for Nakordoni diagnostic anchor privacy."""

from mobile_fuel_stations.diagnostics import _diagnostic_anchor


def test_anchor_diagnostics_exclude_precise_coordinates() -> None:
    anchor = {"lat": 49.123456, "lng": 7.123456, "radius_km": 12, "fuel_type": "e5"}
    result = _diagnostic_anchor(anchor)
    assert result == {"radius_km": 12, "fuel_type": "e5"}
    assert "lat" in anchor and "lng" in anchor


def test_anchor_diagnostics_handle_missing_values() -> None:
    assert _diagnostic_anchor(None) is None
    assert _diagnostic_anchor([]) is None
    assert _diagnostic_anchor({}) == {}
    assert _diagnostic_anchor({"radius_km": 5}) == {"radius_km": 5}
    assert _diagnostic_anchor({"lat": None, "lng": None}) == {}
