"""Offline contract tests for explicit Nakordoni price reports."""

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / "custom_components/mobile_fuel_stations/providers/fuel_report.py"


def load_module():
    # Module contains no Home Assistant dependencies.
    spec = importlib.util.spec_from_file_location("fuel_report_contract", MODULE)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


report = load_module()


def test_prepare_report_explicit_and_normalized():
    result = report.prepare_fuel_report(
        station_id=72571,
        prices=[{"grade": "Diesel", "price": "1.659", "currency": "eur"}],
        dry=True,
    )
    assert result == {
        "station_id": 72571,
        "prices": [{"grade": "diesel", "price": 1.659, "currency": "EUR"}],
        "dry": True,
    }


@pytest.mark.parametrize("station_id", [None, "123", 0, -1, True])
def test_requires_numeric_directory_station_id(station_id):
    with pytest.raises(report.FuelReportValidationError):
        report.prepare_fuel_report(station_id=station_id, prices=[{"grade": "diesel", "price": 1.6, "currency": "EUR"}])


@pytest.mark.parametrize("price", ["nan", "inf", "-inf", -1, 0, True, "wrong"])
def test_rejects_invalid_prices(price):
    with pytest.raises(report.FuelReportValidationError):
        report.prepare_fuel_report(station_id=1, prices=[{"grade": "diesel", "price": price, "currency": "EUR"}])


def test_duplicate_grade_and_maximum():
    item = {"grade": "diesel", "price": 1.5, "currency": "EUR"}
    with pytest.raises(report.FuelReportValidationError):
        report.prepare_fuel_report(station_id=1, prices=[item, item])
    with pytest.raises(report.FuelReportValidationError):
        report.prepare_fuel_report(station_id=1, prices=[{"grade": f"g{i}", "price": 1.5, "currency": "EUR"} for i in range(15)])


def test_observation_age_timezone_and_future():
    now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
    base = {"station_id": 1, "prices": [{"grade": "diesel", "price": 1.5, "currency": "EUR"}], "now": now}
    accepted = report.prepare_fuel_report(**base, observed_at=(now - timedelta(hours=6)).isoformat())
    assert "observed_at" in accepted
    for stamp in [
        (now - timedelta(hours=6, seconds=1)).isoformat(),
        (now + timedelta(seconds=1)).isoformat(),
        "2026-11-02T11:00:00",
        "not-a-date",
    ]:
        with pytest.raises(report.FuelReportValidationError):
            report.prepare_fuel_report(**base, observed_at=stamp)


def test_response_categories():
    result = report.parse_fuel_report_result({
        "ok": True,
        "data": {
            "station_id": 123,
            "accepted": ["diesel"],
            "pending": ["e5"],
            "rejected": [{"grade": "e10", "reason": "currency_mismatch"}],
            "dry": True,
        },
    })
    assert result.accepted == ("diesel",)
    assert result.pending == ("e5",)
    assert result.rejected == (("e10", "currency_mismatch"),)
    assert result.dry is True


@pytest.mark.asyncio
async def test_no_post_without_confirmation():
    class NoPost:
        def post(self, *args, **kwargs):
            raise AssertionError("No POST permitted")
    with pytest.raises(report.FuelReportValidationError, match="confirmation"):
        await report.async_submit_fuel_report(
            NoPost(), api_key="test-key", confirmed_by_user=False,
            station_id=1, prices=[{"grade": "diesel", "price": 1.5, "currency": "EUR"}]
        )
