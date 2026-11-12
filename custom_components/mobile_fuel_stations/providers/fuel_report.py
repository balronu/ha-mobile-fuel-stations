"""Explicit, opt-in Nakordoni fuel price reporting (API v2).

This module never performs background submissions. Callers must obtain an
explicit user confirmation for each submission. No API key or raw response is
persisted or logged.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from aiohttp import ClientSession, ClientTimeout

FUEL_REPORT_URL = "https://nakordoni.eu/api/v2/data/fuel-report"
MAX_PRICES = 14
MAX_OBSERVATION_AGE = timedelta(hours=6)
MAX_PRICE = Decimal("100000")


class FuelReportValidationError(ValueError):
    """A report must be corrected before submission."""


class FuelReportRequestError(Exception):
    """The provider did not accept the HTTP request."""

    def __init__(self, code: str, *, retry_after: int | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.retry_after = retry_after


@dataclass(frozen=True, slots=True)
class FuelReportResult:
    """Non-sensitive provider outcome for the explicit report."""

    station_id: int
    accepted: tuple[str, ...]
    pending: tuple[str, ...]
    rejected: tuple[tuple[str, str], ...]
    observed_at: str | None
    dry: bool


def prepare_fuel_report(
    *,
    station_id: int,
    prices: list[dict[str, Any]],
    observed_at: str | None = None,
    dry: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate an explicitly supplied report; never infer prices from GPS."""
    if isinstance(station_id, bool) or not isinstance(station_id, int) or station_id <= 0:
        raise FuelReportValidationError("A positive Nakordoni directory station_id is required")
    if not isinstance(prices, list) or not 1 <= len(prices) <= MAX_PRICES:
        raise FuelReportValidationError("Supply between 1 and 14 prices")
    if not isinstance(dry, bool):
        raise FuelReportValidationError("dry must be boolean")
    prepared = []
    seen: set[str] = set()
    for item in prices:
        if not isinstance(item, dict):
            raise FuelReportValidationError("Each price must be an object")
        grade = item.get("grade")
        currency = item.get("currency")
        if not isinstance(grade, str) or not grade.strip() or len(grade) > 48:
            raise FuelReportValidationError("A grade name is required")
        grade = grade.strip().lower()
        if grade in seen:
            raise FuelReportValidationError("Duplicate grade in report")
        seen.add(grade)
        if not isinstance(currency, str) or len(currency.strip()) != 3 or not currency.strip().isalpha():
            raise FuelReportValidationError("Currency must be a three-letter ISO code")
        raw_price = item.get("price")
        if isinstance(raw_price, bool):
            raise FuelReportValidationError("Invalid price")
        try:
            price = Decimal(str(raw_price))
        except (InvalidOperation, TypeError, ValueError) as err:
            raise FuelReportValidationError("Invalid price") from err
        if not price.is_finite() or not Decimal("0") < price <= MAX_PRICE:
            raise FuelReportValidationError("Price must be finite and positive")
        prepared.append({"grade": grade, "price": float(price), "currency": currency.strip().upper()})
    payload: dict[str, Any] = {"station_id": station_id, "prices": prepared, "dry": dry}
    if observed_at is not None:
        if not isinstance(observed_at, str):
            raise FuelReportValidationError("observed_at must be ISO 8601")
        try:
            parsed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError as err:
            raise FuelReportValidationError("Invalid observed_at") from err
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise FuelReportValidationError("observed_at must have a timezone offset")
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise FuelReportValidationError("now must be timezone-aware")
        age = current - parsed
        if age < timedelta(0) or age > MAX_OBSERVATION_AGE:
            raise FuelReportValidationError("Observation must be within the last six hours")
        payload["observed_at"] = parsed.isoformat()
    return payload


def parse_fuel_report_result(payload: object) -> FuelReportResult:
    """Parse only documented response fields, not provider secrets."""
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise FuelReportRequestError("provider_error")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise FuelReportRequestError("invalid_response")
    station_id = data.get("station_id")
    if isinstance(station_id, bool) or not isinstance(station_id, int) or station_id <= 0:
        raise FuelReportRequestError("invalid_response")

    def grades(key: str) -> tuple[str, ...]:
        values = data.get(key, [])
        if not isinstance(values, list):
            raise FuelReportRequestError("invalid_response")
        result = []
        for item in values:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict) and isinstance(item.get("grade"), str):
                result.append(item["grade"])
            else:
                raise FuelReportRequestError("invalid_response")
        return tuple(result)

    rejected = data.get("rejected", [])
    if not isinstance(rejected, list):
        raise FuelReportRequestError("invalid_response")
    rejected_items = []
    for item in rejected:
        if not isinstance(item, dict) or not isinstance(item.get("grade"), str) or not isinstance(item.get("reason"), str):
            raise FuelReportRequestError("invalid_response")
        rejected_items.append((item["grade"], item["reason"]))
    observed = data.get("observed_at")
    return FuelReportResult(
        station_id=station_id,
        accepted=grades("accepted"),
        pending=grades("pending"),
        rejected=tuple(rejected_items),
        observed_at=observed if isinstance(observed, str) else None,
        dry=data.get("dry") is True,
    )


async def async_submit_fuel_report(
    session: ClientSession,
    *,
    api_key: str,
    confirmed_by_user: bool,
    station_id: int,
    prices: list[dict[str, Any]],
    observed_at: str | None = None,
    dry: bool = False,
) -> FuelReportResult:
    """Perform exactly one explicit POST; no automatic retries or background calls."""
    if confirmed_by_user is not True:
        raise FuelReportValidationError("Explicit user confirmation required")
    if not isinstance(api_key, str) or not api_key.strip():
        raise FuelReportValidationError("Nakordoni API key required")
    payload = prepare_fuel_report(
        station_id=station_id, prices=prices, observed_at=observed_at, dry=dry
    )
    async with session.post(
        FUEL_REPORT_URL,
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=ClientTimeout(total=15),
    ) as response:
        try:
            result = await response.json(content_type=None)
        except (ValueError, TypeError) as err:
            raise FuelReportRequestError("invalid_response") from err
        if response.status >= 400:
            error = result.get("error") if isinstance(result, dict) else None
            code = error.get("code") if isinstance(error, dict) else None
            allowed = {
                "bad_json", "bad_station_id", "bad_prices", "too_many_prices",
                "bad_observed_at", "observed_at_too_old", "station_not_found",
                "rate_limited", "market_not_allowed", "integration_product_not_allowed",
            }
            safe_code = code if isinstance(code, str) and code in allowed else "provider_error"
            retry = response.headers.get("Retry-After")
            retry_after = int(retry) if isinstance(retry, str) and retry.isdecimal() else None
            raise FuelReportRequestError(safe_code, retry_after=retry_after)
        return parse_fuel_report_result(result)
