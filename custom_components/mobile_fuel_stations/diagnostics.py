"""Diagnostics with secrets and exact coordinates excluded."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_API_KEY,
    CONF_NAKORDONI_API_KEY,
    CONF_PETROMAP_API_KEY,
    CONF_TANKERKOENIG_API_KEY,
    DOMAIN,
)


def _iso(value) -> str | None:
    return value.isoformat() if value is not None else None


def _listener_count(coordinator) -> int | None:
    listeners = getattr(coordinator, "_listeners", None)
    return len(listeners) if isinstance(listeners, dict) else None


def _periodic_refresh_status(coordinator) -> str:
    """Describe the Core callback marker without guessing during refresh."""

    if not hasattr(coordinator, "_unsub_refresh"):
        return "unknown"
    if getattr(coordinator, "_unsub_refresh") is not None:
        return "scheduled"
    # HA Core clears this callback while a refresh is running.  With listeners
    # present, None therefore cannot distinguish an in-flight refresh from a
    # missing schedule; report UNKNOWN instead of a misleading False.
    if _listener_count(coordinator):
        return "unknown"
    return "not_scheduled"


def _periodic_refresh_scheduled(coordinator) -> bool | None:
    """Return a boolean only when the Core callback state is knowable."""

    status = _periodic_refresh_status(coordinator)
    return {"scheduled": True, "not_scheduled": False}.get(status)


def _update_interval_minutes(coordinator) -> float | None:
    interval = getattr(coordinator, "update_interval", None)
    return interval.total_seconds() / 60 if interval is not None else None


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = getattr(entry, "runtime_data", None)
    runtime = {
        "nakordoni_last_request": hass.data.get(DOMAIN, {})
        .get("last_request_diagnostics", {})
        .get(entry.entry_id),
    }
    if coordinator is not None:
        runtime.update({
            "coordinator_instance_id": f"{id(coordinator):x}",
            "coordinator_listener_count": _listener_count(coordinator),
            "coordinator_update_interval_minutes": _update_interval_minutes(coordinator),
            "fetch_mode": getattr(coordinator, "fetch_mode", "automatic"),
            "manual_refresh_in_progress": getattr(coordinator, "_manual_refresh_in_progress", False),
            "periodic_refresh_scheduled": _periodic_refresh_scheduled(coordinator),
            "periodic_refresh_callback_status": _periodic_refresh_status(coordinator),
            # HA Core stores only a cancellation callback, not the TimerHandle.
            # A deadline is therefore intentionally UNKNOWN rather than guessed.
            "next_refresh_deadline": None,
            "gps_available": getattr(coordinator, "gps_available", None),
            "adaptive_updates_enabled": getattr(coordinator, "adaptive_updates_enabled", False),
            "adaptive_update_interval_minutes": _update_interval_minutes(coordinator)
            if getattr(coordinator, "adaptive_updates_enabled", False)
            else None,
            "last_gps_speed_kmh": getattr(
                getattr(coordinator, "last_gps_sample", None), "speed_kmh", None
            ),
            "gps_listener_registered": getattr(coordinator, "gps_listener_registered", None),
            "last_successful_update": _iso(coordinator.last_successful_update),
            "last_update_attempt": _iso(getattr(coordinator, "last_update_attempt", None)),
            "last_update_result": getattr(coordinator, "last_update_result", None),
            "last_update_error_class": getattr(coordinator, "last_update_error_class", None),
            "last_update_error_code": getattr(coordinator, "last_update_error_code", None),
            "last_update_error_provider": getattr(coordinator, "last_update_error_provider", None),
            "data_stale": getattr(coordinator, "data_stale", None),
            "stale_price_count": sum(
                1 for station in (getattr(coordinator, "data", None) or []) if getattr(station, "price_stale", None) is True
            ),
            "last_provider_attempt": _iso(getattr(coordinator, "last_provider_attempt", None)),
            "last_provider_success": _iso(getattr(coordinator, "last_provider_success", None)),
            "effective_provider": getattr(coordinator, "diagnostic_effective_provider", None),
            "configured_providers": sorted(getattr(coordinator, "provider_modes", ())),
            "provider_selection_mode": (
                "auto" if getattr(coordinator, "_is_auto", False)
                else getattr(coordinator, "options", {}).get("provider_mode")
            ),
            "provider_selection_reason": getattr(
                coordinator, "diagnostic_provider_selection_reason", None
            ),
            "fallback_attempted": getattr(coordinator, "fallback_attempted", False),
            "fallback_provider": getattr(coordinator, "fallback_provider", None),
            "fallback_result": getattr(coordinator, "fallback_result", None),
            "fallback_skip_reason": getattr(coordinator, "fallback_skip_reason", None),
            "provider_cooldown_remaining": getattr(
                coordinator, "diagnostic_provider_cooldown_remaining", None
            ),
            "provider_cooldowns": getattr(
                coordinator, "diagnostic_provider_cooldowns", {}
            ),
            "provider_availability": getattr(
                coordinator, "diagnostic_provider_availability", {}
            ),
            "manual_refresh_available": getattr(
                coordinator, "diagnostic_manual_refresh_available", False
            ),
            "manual_refresh_retry_seconds": getattr(
                coordinator, "diagnostic_manual_refresh_retry_seconds", 0
            ),
            "manual_refresh_blocked_reason": getattr(
                coordinator, "diagnostic_manual_refresh_blocked_reason", None
            ),
            "country_context": getattr(
                coordinator, "diagnostic_country_context", {}
            ),
            "next_provider": getattr(coordinator, "diagnostic_next_provider", None),
            "next_provider_retry": _iso(
                getattr(coordinator, "diagnostic_next_provider_retry", None)
            ),
            "cache_valid": getattr(coordinator, "_has_valid_provider_result", False),
            "cache_provider": getattr(coordinator, "_cache_provider", None),
            "credential_mode": getattr(coordinator, "diagnostic_credential_mode", None),
            "market_status": getattr(coordinator, "diagnostic_market_status", None),
            "markets_approved": getattr(coordinator, "diagnostic_markets_approved", []),
            "markets_granted": getattr(coordinator, "diagnostic_markets_granted", []),
            "markets_allowed": getattr(coordinator, "diagnostic_markets_allowed", []),
            "markets_available": getattr(coordinator, "diagnostic_markets_available", []),
            "upgrade_url": getattr(coordinator, "nakordoni_upgrade_url", None),
            "coverage_countries": getattr(coordinator, "nakordoni_coverage_countries", []),
            "coverage_fuels": getattr(coordinator, "nakordoni_coverage_fuels", []),
            "coverage_status": getattr(coordinator, "nakordoni_coverage_status", "unknown"),
            "coverage_station_countries": getattr(coordinator, "nakordoni_coverage_station_countries", []),
            "coverage_station_counts": getattr(coordinator, "nakordoni_coverage_station_counts", {}),
            "coverage_sparse": list(getattr(getattr(coordinator, "nakordoni_response_metadata", None), "sparse_coverage", ())),
            "coverage_measured_at": _iso(getattr(getattr(coordinator, "nakordoni_response_metadata", None), "coverage_measured_at", None)),
            "coverage_fuel_type_note": getattr(getattr(coordinator, "nakordoni_response_metadata", None), "fuel_type_note", None),
            "markets_filtered": getattr(getattr(coordinator, "nakordoni_response_metadata", None), "markets_filtered", None),
            "markets_notice": getattr(getattr(coordinator, "nakordoni_response_metadata", None), "markets_notice", None),
            "anchor": getattr(getattr(coordinator, "nakordoni_response_metadata", None), "anchor", None),
            "quota": getattr(coordinator, "diagnostic_quota", {"limit": None, "remaining": None}),
            "nakordoni_account_usage": (
                coordinator.nakordoni_account_usage.as_diagnostics()
                if getattr(coordinator, "nakordoni_account_usage", None) is not None
                else None
            ),
            "nakordoni_usage_last_attempt": _iso(getattr(coordinator, "nakordoni_usage_last_attempt", None)),
            "nakordoni_usage_last_success": _iso(getattr(coordinator, "nakordoni_usage_last_success", None)),
            "nakordoni_usage_error": getattr(coordinator, "nakordoni_usage_error", None),
            "nakordoni_usage_error_at": _iso(getattr(coordinator, "nakordoni_usage_error_at", None)),
            "nakordoni_usage_upgrade_url": getattr(coordinator, "nakordoni_usage_upgrade_url", None),
            "nakordoni_usage_pass_url": getattr(coordinator, "nakordoni_usage_pass_url", None),
            "nakordoni_usage_reset_at": _iso(getattr(coordinator, "nakordoni_usage_reset_at", None)),
            "startup_recovery_status": getattr(coordinator, "recovery_status", None),
            "recovery_task_status": getattr(coordinator, "recovery_task_status", None),
            "recovery_attempt_count": getattr(coordinator, "recovery_attempt_count", 0),
            "recovery_trigger": getattr(coordinator, "recovery_trigger", None),
            "recovery_next_retry_at": _iso(
                getattr(coordinator, "recovery_next_retry_at", None)
            ),
            "recovery_last_gps_event_type": getattr(
                coordinator, "recovery_last_gps_event_type", None
            ),
            "recovery_last_gps_event_at": _iso(
                getattr(coordinator, "recovery_last_gps_event_at", None)
            ),
            "recovery_provider_in_flight": getattr(
                coordinator, "recovery_provider_in_flight", False
            ),
            "recovery_error_class": getattr(coordinator, "recovery_error_class", None),
            "last_update_success": getattr(coordinator, "last_update_success", None),
            "result_count": len(coordinator.data or []),
            "error": type(coordinator.last_exception).__name__
            if coordinator.last_exception else None,
        })
    return {
        "version": 2,
        "config": {
            key: value
            for key, value in {**entry.data, **entry.options}.items()
            if key not in {
                CONF_API_KEY,
                CONF_TANKERKOENIG_API_KEY,
                CONF_PETROMAP_API_KEY,
                CONF_NAKORDONI_API_KEY,
                "token",
            }
            and "coordinate" not in key
            and key not in {"latitude", "longitude"}
        },
        "runtime": runtime,
    }
