from types import SimpleNamespace

import pytest

from mobile_fuel_stations.api import Station
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
        },
        reference_position=None,
        last_successful_update=None,
        current_distance_km=None,
    )
    overview = object.__new__(sensor.OverviewSensor)
    overview.coordinator = coordinator
    overview.hass = object()
    overview._entry = SimpleNamespace(entry_id="entry-a")

    attributes = overview.extra_state_attributes

    assert attributes["radius"] == 20
    assert attributes["fuel_type"] == "diesel"
    assert attributes["location_entity"] == "device_tracker.my_vehicle"
    assert attributes["station_count"] == 1
    assert attributes["station_entities"] == [
        "sensor.vehicle_station_1",
        "sensor.vehicle_station_2",
    ]


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
        "station_id": "Demo Station",
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
