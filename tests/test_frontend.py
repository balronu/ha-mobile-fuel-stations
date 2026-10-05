import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from mobile_fuel_stations import DOMAIN
from mobile_fuel_stations import async_setup
from mobile_fuel_stations.const import (
    FRONTEND_FILENAME,
    FRONTEND_RESOURCE_URL,
    FRONTEND_URL,
    FRONTEND_VERSION,
)


def test_frontend_static_path_is_registered_once():
    register = AsyncMock()
    hass = SimpleNamespace(data={}, http=SimpleNamespace(async_register_static_paths=register))

    assert asyncio.run(async_setup(hass, {})) is True
    assert asyncio.run(async_setup(hass, {})) is True

    register.assert_awaited_once()
    config = register.await_args.args[0][0]
    assert config.url_path == f"/{DOMAIN}"
    assert config.path.endswith(f"custom_components/{DOMAIN}/frontend")
    assert config.cache_headers is True


def test_frontend_bundle_and_versioned_resource_url():
    bundle = Path(__file__).parents[1] / "custom_components" / DOMAIN / "frontend" / FRONTEND_FILENAME
    assert bundle.is_file()
    assert bundle.stat().st_size > 1000
    assert FRONTEND_URL == f"/{DOMAIN}/{FRONTEND_FILENAME}"
    assert FRONTEND_RESOURCE_URL == f"{FRONTEND_URL}?v={FRONTEND_VERSION}"


def test_frontend_resource_url_is_deterministic():
    assert FRONTEND_RESOURCE_URL == "/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.1.0"
