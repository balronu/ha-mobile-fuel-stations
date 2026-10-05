import { beforeEach, describe, expect, it } from "vitest";
import { discoverStationEntities, formatDistance, formatPrice, MobileFuelStationsCard } from "../src/mobile-fuel-stations-card";

const overviewId = "sensor.vehicle_nearby_stations";
const state = (value: string, attributes: Record<string, unknown> = {}) => ({ state: value, attributes });
const hassFor = (count: number, attrs: Record<string, unknown> = {}, stationAttrs: Record<string, unknown> = {}) => {
  const states: Record<string, ReturnType<typeof state>> = { [overviewId]: state("3", { station_count: count, station_entities: Array.from({ length: count }, (_, i) => `sensor.vehicle_station_${i + 1}`), ...attrs }) };
  for (let i = 1; i <= count; i++) states[`sensor.vehicle_station_${i}`] = state(String(1.5 + i / 100), { station_name: `Station ${i}`, distance: i, is_open: true, ...stationAttrs });
  return { states };
};

describe("formatting and discovery", () => {
  it("formats prices and distances with stable units", () => { expect(formatPrice("1.659")).toBe("1,659 €/l"); expect(formatDistance(1.25)).toBe("1,3 km"); });
  it("keeps station_entities order and ignores unavailable slots", () => {
    const hass = { states: { a: state("1"), b: state("unavailable"), c: state("3") } };
    expect(discoverStationEntities(overviewId, state("3", { station_entities: ["a", "b", "c"] }), hass)).toEqual(["a", "c"]);
  });
  it("supports the v0.1 same-prefix fallback without mixing entries", () => {
    const hass = { states: { "sensor.vehicle_station_1": state("1"), "sensor.other_station_1": state("2") } };
    expect(discoverStationEntities(overviewId, state("1", { station_count: 1 }), hass)).toEqual(["sensor.vehicle_station_1"]);
  });
});

describe("card", () => {
  beforeEach(() => { document.body.innerHTML = ""; });
  it("rejects missing entity configuration", () => { const card = new MobileFuelStationsCard(); expect(() => card.setConfig({ type: "custom:mobile-fuel-stations-card" })).toThrow(/entity/); });
  it("renders overview, one, five and ten stations in order", async () => {
    for (const count of [1, 5, 10]) { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ type: "custom:mobile-fuel-stations-card", entity: overviewId }); card.hass = hassFor(count); await card.updateComplete; expect(card.shadowRoot?.querySelectorAll(".station")).toHaveLength(count); expect(card.shadowRoot?.textContent).toContain("Station 1"); }
  });
  it("renders unavailable slots and all-unavailable states safely", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); const hass = hassFor(2); hass.states["sensor.vehicle_station_1"]!.state = "unavailable"; card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.querySelectorAll(".station")).toHaveLength(1);
    hass.states["sensor.vehicle_station_2"]!.state = "unavailable"; card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("Keine Tankstellen gefunden");
  });
  it("handles missing price, address, distance, and is_open without inventing values", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); const hass = hassFor(1); hass.states["sensor.vehicle_station_1"] = state("not-a-price", { station_name: "No Details" }); card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("Preis nicht verfügbar"); expect(card.shadowRoot?.textContent).not.toContain("Geöffnet"); expect(card.shadowRoot?.textContent).not.toContain("km");
  });
  it("shows open and closed states", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); const hass = hassFor(1); hass.states["sensor.vehicle_station_1"]!.attributes.is_open = false; card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("Geschlossen"); });
  it("renders required error states", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: "sensor.missing" }); card.hass = { states: {} }; await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("Overview entity not found"); card.hass = { states: { [overviewId]: state("unavailable") } }; card.setConfig({ entity: overviewId }); await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("nicht verfügbar"); });
  it("dispatches more-info with the station entity id", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); card.hass = hassFor(1); await card.updateComplete; let event: Event | undefined; card.addEventListener("hass-more-info", (value) => { event = value; }); (card.shadowRoot?.querySelector(".station") as HTMLElement).click(); expect((event as CustomEvent).detail.entityId).toBe("sensor.vehicle_station_1"); });
});
