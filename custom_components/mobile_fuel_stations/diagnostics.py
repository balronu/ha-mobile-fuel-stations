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
            "periodic_refresh_scheduled": _periodic_refresh_scheduled(coordinator),
            "periodic_refresh_callback_status": _periodic_refresh_status(coordinator),
            # HA Core stores only a cancellation callback, not the TimerHandle.
            # A deadline is therefore intentionally UNKNOWN rather than guessed.
            "next_refresh_deadline": None,
            "gps_available": getattr(coordinator, "gps_available", None),
            "gps_listener_registered": getattr(coordinator, "gps_listener_registered", None),
            "last_successful_update": _iso(coordinator.last_successful_update),
            "last_update_attempt": _iso(getattr(coordinator, "last_update_attempt", None)),
            "last_update_result": getattr(coordinator, "last_update_result", None),
            "last_provider_attempt": _iso(getattr(coordinator, "last_provider_attempt", None)),
            "last_provider_success": _iso(getattr(coordinator, "last_provider_success", None)),
            "startup_recovery_status": getattr(coordinator, "recovery_status", None),
            "recovery_task_status": getattr(coordinator, "recovery_task_status", None),
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
            }
            and "coordinate" not in key
            and key not in {"latitude", "longitude"}
        },
        "runtime": runtime,
    }
