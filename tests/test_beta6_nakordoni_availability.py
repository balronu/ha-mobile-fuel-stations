"""Beta.6 provider preflight and fallback availability regressions."""

from datetime import datetime, timedelta
from types import SimpleNamespace

from mobile_fuel_stations.const import (
    CONF_PROVIDER_MODE,
    FETCH_MODE_MANUAL,
    PROVIDER_AUTO,
    PROVIDER_NAKORDONI,
    PROVIDER_TANKERKOENIG,
)
from mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator
from mobile_fuel_stations.providers.nakordoni import (
    NakordoniAccountUsage,
    NakordoniMarketAccess,
    NakordoniQuota,
)


def _coordinator(*, markets=(), remaining=10, usage_present=True):
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.options = {CONF_PROVIDER_MODE: PROVIDER_AUTO}
    coordinator.fetch_mode = FETCH_MODE_MANUAL
    coordinator._manual_refresh_in_progress = False
    coordinator.provider_modes = frozenset({PROVIDER_TANKERKOENIG, PROVIDER_NAKORDONI})
    coordinator.fuel_types = ["diesel"]
    coordinator.available_provider_modes = coordinator.provider_modes
    coordinator.provider_last_requests = {
        PROVIDER_TANKERKOENIG: datetime.now().astimezone(),
    }
    coordinator.provider_retry_not_before = {}
    coordinator.country_auto_context = SimpleNamespace(confirmed_country="DE")
    coordinator.nakordoni_market_access = NakordoniMarketAccess(markets_approved=tuple(markets))
    coordinator.nakordoni_market_access_source = "usage" if markets else "unknown"
    coordinator.nakordoni_market_access_checked_at = datetime.now().astimezone()
    coordinator.nakordoni_account_usage = (
        NakordoniAccountUsage(quotas={"cheap": NakordoniQuota(100, 1, remaining)})
        if usage_present else None
    )
    coordinator.nakordoni_usage_last_success = datetime.now().astimezone()
    return coordinator


def test_tankerkoenig_cooldown_allows_confirmed_nakordoni_market():
    coordinator = _coordinator(markets=("DE",), remaining=10)

    assert coordinator.diagnostic_manual_refresh_available is True
    assert coordinator.diagnostic_manual_refresh_retry_seconds == 0
    assert coordinator.diagnostic_provider_availability[PROVIDER_TANKERKOENIG]["status"] == "cooldown"
    assert coordinator.diagnostic_provider_availability[PROVIDER_NAKORDONI]["available"] is True


def test_unknown_nakordoni_market_does_not_create_fallback():
    coordinator = _coordinator(markets=(), remaining=10)

    assert coordinator.diagnostic_manual_refresh_available is False
    assert coordinator.diagnostic_manual_refresh_retry_seconds > 0
    assert coordinator.diagnostic_provider_availability[PROVIDER_NAKORDONI]["status"] == "coverage_unknown"
    assert "coverage_unknown" in coordinator.diagnostic_manual_refresh_blocked_reason


def test_manual_nakordoni_selection_also_requires_confirmed_market():
    coordinator = _coordinator(markets=(), remaining=10)
    coordinator.options[CONF_PROVIDER_MODE] = PROVIDER_NAKORDONI

    assert coordinator.diagnostic_manual_refresh_available is False
    assert coordinator.diagnostic_provider_availability[PROVIDER_NAKORDONI]["status"] == "coverage_unknown"


def test_zero_nakordoni_quota_is_not_available_but_unknown_quota_is_allowed():
    exhausted = _coordinator(markets=("DE",), remaining=0)
    assert exhausted.diagnostic_manual_refresh_available is False
    assert exhausted.diagnostic_provider_availability[PROVIDER_NAKORDONI]["status"] == "quota_exhausted"

    unknown = _coordinator(markets=("DE",), usage_present=False)
    assert unknown.diagnostic_manual_refresh_available is True
    assert unknown.diagnostic_provider_availability[PROVIDER_NAKORDONI]["status"] == "quota_unknown"


def test_stale_usage_market_metadata_is_conservative():
    coordinator = _coordinator(markets=("DE",), remaining=10)
    coordinator.nakordoni_market_access_checked_at = (
        datetime.now().astimezone() - timedelta(minutes=16)
    )

    assert coordinator.diagnostic_manual_refresh_available is False
    assert coordinator.diagnostic_provider_availability[PROVIDER_NAKORDONI]["status"] == "coverage_unknown"
