import asyncio

from mobile_fuel_stations.const import CONF_NAKORDONI_API_KEY, PROVIDER_NAKORDONI
from mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator
from mobile_fuel_stations.providers.nakordoni import NakordoniAccountUsage, NakordoniQuota


class UsageProvider:
    def __init__(self):
        self.calls = 0

    async def async_get_account_usage(self):
        self.calls += 1
        return NakordoniAccountUsage(
            quotas={"cheap": NakordoniQuota(100, 1, 99)},
            upgrade_url="https://example.invalid/upgrade",
        )


def coordinator_for_usage(provider):
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.provider_modes = frozenset({PROVIDER_NAKORDONI})
    coordinator.options = {CONF_NAKORDONI_API_KEY: "secret"}
    coordinator._oauth_session = None
    coordinator._get_provider = lambda mode: provider
    coordinator.nakordoni_account_usage = None
    coordinator.nakordoni_usage_last_attempt = None
    coordinator.nakordoni_usage_last_success = None
    coordinator.nakordoni_usage_error = None
    coordinator.nakordoni_usage_error_at = None
    coordinator.nakordoni_usage_upgrade_url = None
    coordinator.nakordoni_usage_pass_url = None
    coordinator.nakordoni_usage_reset_at = None
    return coordinator


def test_account_usage_is_never_polled_more_often_than_15_minutes():
    provider = UsageProvider()
    coordinator = coordinator_for_usage(provider)

    asyncio.run(coordinator.async_update_nakordoni_usage())
    asyncio.run(coordinator.async_update_nakordoni_usage())

    assert provider.calls == 1
    assert coordinator.nakordoni_account_usage.cheap.remaining == 99
    assert coordinator.nakordoni_usage_upgrade_url == "https://example.invalid/upgrade"

    asyncio.run(coordinator.async_update_nakordoni_usage(force=True))
    assert provider.calls == 2


def test_usage_snapshot_round_trips_without_secrets():
    provider = UsageProvider()
    coordinator = coordinator_for_usage(provider)
    asyncio.run(coordinator.async_update_nakordoni_usage())

    snapshot = coordinator._nakordoni_usage_to_store()
    restored = coordinator_for_usage(provider)
    restored._restore_nakordoni_usage(snapshot)

    assert restored.nakordoni_account_usage.cheap.remaining == 99
    assert restored.nakordoni_usage_last_success is not None
    assert "secret" not in repr(snapshot).lower()
