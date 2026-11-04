from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "tessera-plugin"
SOURCE = (PLUGIN / "components/mobile_fuel_stations/mobile_fuel_stations.cpp").read_text()


def test_tessera_manifest_exposes_supported_resize_range_and_card():
    manifest = yaml.safe_load((PLUGIN / "tessera-plugin.yaml").read_text())
    tile = manifest["tiles"][0]

    assert tile["sizes"] == {"min": "1x1", "max": "4x4"}
    assert any(card["id"] == "stations" for card in manifest["cards"])


def test_highlights_tile_opens_detail_card_for_every_supported_size():
    tile_source = SOURCE.split("class HighlightsTile", 1)[1].split("class MobileFuelStationsCard", 1)[0]
    method = tile_source.split("  void on_tap() override {", 1)[1].split("  void on_theme() override", 1)[0]

    assert 'tessera::open_card(plugin_->plugin_id(), "stations", entity_, tile_);' in method
    assert "single_row_" not in method
    assert "show_cheapest_" not in tile_source


def test_plugin_setup_registers_matching_tile_and_card_ids():
    assert 'add_tile("highlights"' in SOURCE
    assert 'add_card("stations"' in SOURCE
