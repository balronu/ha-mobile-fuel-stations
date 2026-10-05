import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

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

    with patch("mobile_fuel_stations.add_extra_js_url") as add_extra_js:
        assert asyncio.run(async_setup(hass, {})) is True
        assert asyncio.run(async_setup(hass, {})) is True

    register.assert_awaited_once()
    add_extra_js.assert_called_once_with(hass, FRONTEND_URL)
    config = register.await_args.args[0][0]
    assert config.url_path == f"/{DOMAIN}"
    assert config.path.endswith(f"custom_components/{DOMAIN}/frontend")
    assert config.cache_headers is False


def test_frontend_extra_module_registration_is_integration_wide():
    register = AsyncMock()
    hass = SimpleNamespace(data={}, http=SimpleNamespace(async_register_static_paths=register))

    with patch("mobile_fuel_stations.add_extra_js_url") as add_extra_js:
        assert asyncio.run(async_setup(hass, {})) is True
        assert asyncio.run(async_setup(hass, {})) is True

    assert add_extra_js.call_count == 1
    assert add_extra_js.call_args.args == (hass, FRONTEND_URL)


def test_frontend_bundle_and_versioned_resource_url():
    bundle = Path(__file__).parents[1] / "custom_components" / DOMAIN / "frontend" / FRONTEND_FILENAME
    assert bundle.is_file()
    assert bundle.stat().st_size > 1000
    bundle_text = bundle.read_text()
    assert 'customElements.get("mobile-fuel-stations-card")' in bundle_text
    assert 'customElements.get("mobile-fuel-stations-card-editor")' in bundle_text
    assert FRONTEND_URL == f"/{DOMAIN}/{FRONTEND_FILENAME}"
    assert FRONTEND_RESOURCE_URL == FRONTEND_URL
    assert "?" not in FRONTEND_URL


def test_frontend_resource_url_is_stable_across_updates():
    assert FRONTEND_RESOURCE_URL == "/mobile_fuel_stations/mobile-fuel-stations-card.js"


def test_stable_versions_are_synchronized():
    root = Path(__file__).parents[1]
    manifest = json.loads(
        (root / "custom_components" / DOMAIN / "manifest.json").read_text()
    )
    package = json.loads((root / "frontend" / "package.json").read_text())
    assert manifest["version"] == FRONTEND_VERSION == package["version"] == "0.3.0"
