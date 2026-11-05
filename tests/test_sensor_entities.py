from types import SimpleNamespace

import pytest

from mobile_fuel_stations.api import Station
from mobile_fuel_stations.const import CONF_PROVIDER_MODE, PROVIDER_AUTO, PROVIDER_NAKORDONI, PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG
from mobile_fuel_stations import sensor


class FakeEntityRegistry:
    def __init__(self, entities):
        self.entities = entities

    def async_get_entity_id(self, domain, platform, unique_id):
        return self.entities.get((domain, platform, unique_id))


def registered_ids(monkeypatch, slot_count, entry_id="entry-a"):
    entities = {
        ("sensor", sensor.DOMAIN, f"{entry_id}_station_slot_{index}"): f"sensor.vehicle_station_{index}"
        for index in range(1, slot_count + 1)
    }
    monkeypatch.setattr(sensor.er, "async_get", lambda hass: FakeEntityRegistry(entities))
    return sensor._registered_station_entity_ids(
        object(), SimpleNamespace(entry_id=entry_id), slot_count
    )


@pytest.mark.parametrize("slot_count", [1, 5, 10])
def test_registered_station_entity_ids_preserve_slot_count_and_order(monkeypatch, slot_count):
    assert registered_ids(monkeypatch, slot_count) == [
        f"sensor.vehicle_station_{index}" for index in range(1, slot_count + 1)
    ]


def test_station_entities_include_configured_empty_slots(monkeypatch):
    assert registered_ids(monkeypatch, 5) == [
        "sensor.vehicle_station_1",
        "sensor.vehicle_station_2",
        "sensor.vehicle_station_3",
        "sensor.vehicle_station_4",
        "sensor.vehicle_station_5",
    ]


def test_multiple_config_entries_do_not_mix_station_entities(monkeypatch):
    entities = {
        ("sensor", sensor.DOMAIN, "entry-a_station_slot_1"): "sensor.vehicle_a_station_1",
        ("sensor", sensor.DOMAIN, "entry-b_station_slot_1"): "sensor.vehicle_b_station_1",
    }
    monkeypatch.setattr(sensor.er, "async_get", lambda hass: FakeEntityRegistry(entities))

    assert sensor._registered_station_entity_ids(
        object(), SimpleNamespace(entry_id="entry-a"), 1
    ) == ["sensor.vehicle_a_station_1"]
    assert sensor._registered_station_entity_ids(
        object(), SimpleNamespace(entry_id="entry-b"), 1
    ) == ["sensor.vehicle_b_station_1"]


def test_overview_attributes_keep_existing_fields_and_add_station_entities(monkeypatch):
    monkeypatch.setattr(
        sensor,
        "_registered_station_entity_ids",
        lambda hass, entry, count: ["sensor.vehicle_station_1", "sensor.vehicle_station_2"],
    )
    coordinator = SimpleNamespace(
        data=[object()],
        config={
            "radius": 20,
            "fuel_type": "diesel",
            "location_entity": "device_tracker.my_vehicle",
            "station_count": 2,
            "provider_mode": PROVIDER_TANKERKOENIG,
        },
        reference_position=None,
        last_successful_update=None,
        current_distance_km=None,
        nearest_station=None,
        cheapest_station=None,
    )
    overview = object.__new__(sensor.OverviewSensor)
    overview.coordinator = coordinator
    overview.hass = object()
    overview._entry = SimpleNamespace(entry_id="entry-a")

    attributes = overview.extra_state_attributes

    assert attributes["radius"] == 20
    assert attributes["fuel_type"] == "diesel"
    assert attributes["sort_mode"] == "distance"
    assert attributes["sort_fuel"] == "diesel"
    assert attributes["location_entity"] == "device_tracker.my_vehicle"
    assert attributes["station_count"] == 1
    assert attributes["station_entities"] == [
        "sensor.vehicle_station_1",
        "sensor.vehicle_station_2",
    ]
    assert attributes["nearest_station"] is None
    assert attributes["cheapest_station"] is None


def test_station_slot_state_and_attributes_remain_unchanged():
    station = Station(
        "demo-id",
        "Demo Station",
        "Demo Brand",
        1.799,
        2.4,
        True,
        "Example Street",
        "1",
        "12345",
        "Demo Town",
        50.0,
        8.0,
    )
    slot = object.__new__(sensor.StationSlotSensor)
    slot.index = 0
    slot.coordinator = SimpleNamespace(data=[station])

    assert slot.native_value == 1.799
    assert slot.extra_state_attributes == {
        "station_id": "demo-id",
        "station_name": "Demo Station",
        "brand": "Demo Brand",
        "distance": 2.4,
        "is_open": True,
        "street": "Example Street",
        "house_number": "1",
        "postcode": "12345",
        "place": "Demo Town",
        "latitude": 50.0,
        "longitude": 8.0,
    }


def test_station_slot_name_follows_station_without_changing_unique_id():
    first = Station("first", "First Station", "Brand", 1.7, 1.0, True, "Street", "1", "1", "Town", 50.0, 8.0)
    second = Station("second", "Second Station", "Brand", 1.8, 2.0, True, "Street", "2", "2", "Town", 50.1, 8.1)
    slot = object.__new__(sensor.StationSlotSensor)
    slot.index = 0
    slot._attr_unique_id = "entry-a_station_slot_1"
    slot.coordinator = SimpleNamespace(data=[first])

    assert slot.name == "First Station"
    assert slot._attr_unique_id == "entry-a_station_slot_1"
    slot.coordinator.data = [second]
    assert slot.name == "Second Station"
    assert slot._attr_unique_id == "entry-a_station_slot_1"


@pytest.mark.parametrize(
    ("provider_mode", "manufacturer"),
    [
        (None, "Tankerkönig"),
        (PROVIDER_TANKERKOENIG, "Tankerkönig"),
        (PROVIDER_PETROMAP, "Petromap"),
        (PROVIDER_AUTO, "Mobile Fuel Stations"),
        (PROVIDER_NAKORDONI, "Nakordoni"),
    ],
)
def test_device_manufacturer_follows_mode_without_changing_identifier(
    provider_mode, manufacturer
):
    data = {"entry_id": "entry-a", "title": "Vehicle stations", "data": {}, "options": {}}
    if provider_mode is not None:
        data["data"][CONF_PROVIDER_MODE] = provider_mode
    entry = SimpleNamespace(**data)

    info = sensor._device_info(entry)

    assert info["manufacturer"] == manufacturer
    assert info["identifiers"] == {(sensor.DOMAIN, "entry-a")}


def test_tessera_vehicle_feed_isolated_and_fresh():
    vehicle_a = Station(
        "a", "JET", "JET", 1.799, 2.4, True,
        "Road", "12", "12345", "Saarbrücken", 49.0, 7.0,
        currency="EUR", fuel_type="diesel",
        fuel_prices={"diesel": 1.799, "e10": 1.699, "e5": 1.759},
    )
    vehicle_b = Station(
        "b", "Shell", "Shell", 1.899, 5.0, None,
        "Other", "1", "23456", "Berlin", 52.0, 13.0,
        currency="EUR", fuel_type="diesel",
    )
    a = sensor._tessera_station_attributes([vehicle_a], vehicle="Wohnmobil", data_stale=False)
    b = sensor._tessera_station_attributes([vehicle_b], vehicle="PKW", data_stale=False)
    assert a["tessera_vehicle"] == "Wohnmobil"
    assert b["tessera_vehicle"] == "PKW"
    assert a["tessera_names"] == ["JET"]
    assert b["tessera_names"] == ["Shell"]
    assert a["tessera_places"] == ["2.4 km · Saarbrücken"]
    assert a["tessera_open"] == [1]
    assert b["tessera_open"] == [-1]
    assert a["tessera_diesel"] == [1.799]
    assert a["tessera_e10"] == [1.699]
    assert b["tessera_diesel"] == [1.899]
    assert sensor._tessera_station_attributes([vehicle_a], vehicle="Wohnmobil", data_stale=True)["tessera_diesel"] == [0.0]


def test_tessera_feed_rejects_wrong_currency_fallback_invalid_and_old_prices():
    fallback = Station(
        "x", "Fallback", "Fallback", 1.9, None, True,
        "", "", "", "", None, None,
        currency="EUR",
        fuel_prices={"e10": 1.9, "diesel": -1},
        fuel_fallbacks={"e10": True},
    )
    foreign = Station(
        "y", "Foreign", "Foreign", 4.5, None, False,
        "", "", "", "", None, None,
        currency="PLN", fuel_type="diesel",
    )
    old = Station(
        "z", "Old", "Old", 1.5, None, True,
        "", "", "", "", None, None,
        currency="EUR", fuel_type="diesel", price_stale=True,
    )
    output = sensor._tessera_station_attributes([fallback, foreign, old], vehicle="Van", data_stale=False)
    assert output["tessera_diesel"] == [0.0, 0.0, 0.0]
    assert output["tessera_e10"] == [0.0, 0.0, 0.0]
    assert output["tessera_open"] == [1, 0, 1]


def test_tessera_station_feed_bounded_and_parallel():
    many = [
        Station(
            str(index), f"Station {index}", "", 1.8, None, True,
            "", "", "", "", None, None,
            currency="EUR", fuel_type="diesel"
        )
        for index in range(14)
    ]
    values = sensor._tessera_station_attributes(many, vehicle="Test", data_stale=False)
    for key in ("tessera_names", "tessera_places", "tessera_open", "tessera_diesel", "tessera_e10", "tessera_e5"):
        assert len(values[key]) == 10
    assert values["tessera_names"][-1] == "Station 9"
    assert sensor._tessera_station_attributes([], vehicle="Empty", data_stale=False)["tessera_names"] == []


