import { beforeEach, describe, expect, it } from "vitest";
import { buildNavigationUrl, detectNavigationProvider, discoverStationEntities, formatDistance, formatPrice, MobileFuelStationsCard, shouldShowBrand } from "../src/mobile-fuel-stations-card";

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
  it("suppresses duplicate brands but keeps additional brand information", () => {
    expect(shouldShowBrand("Tankstelle Winkler", "Winkler")).toBe(false);
    expect(shouldShowBrand("Auto Wahl Sport Illingen", "Auto Wahl Sport")).toBe(false);
    expect(shouldShowBrand("Tankstelle", "Shell")).toBe(true);
    expect(shouldShowBrand("Winkler-St. Ingbert", "Winkler 24h")).toBe(true);
    expect(shouldShowBrand("OEL Schneider GmbH Rodenhof", "OEL")).toBe(false);
  });
  it("selects navigation providers defensively and URL-encodes targets", () => {
    expect(buildNavigationUrl(49.123, 8.456)).toBe("https://www.google.com/maps/dir/?api=1&destination=49.123%2C8.456&travelmode=driving&dir_action=navigate");
    expect(buildNavigationUrl(49.123, 8.456, "apple", "Tankstelle Ä")).toBe("https://maps.apple.com/directions?destination=49.123%2C8.456&mode=driving");
    expect(buildNavigationUrl(49.123, 8.456, "google", "Tankstelle Ä")).toContain("google.com/maps/dir/");
    expect(buildNavigationUrl(49.123, 8.456, "google")).not.toContain("origin=");
    expect(buildNavigationUrl(49.123, 8.456, "waze")).toBe("https://www.waze.com/ul?ll=49.123%2C8.456&navigate=yes");
    expect(buildNavigationUrl(49.123, 8.456, "waze")).not.toContain("waze://");
    expect(buildNavigationUrl(49.123, 8.456, "waze")).not.toContain("origin=");
    expect(detectNavigationProvider("auto", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)")).toBe("apple");
    expect(detectNavigationProvider("auto", "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)")).toBe("apple");
    expect(detectNavigationProvider("auto", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", 5)).toBe("apple");
    expect(detectNavigationProvider("auto", "Mozilla/5.0 (Linux; Android 14; Pixel)")).toBe("google");
    expect(detectNavigationProvider("auto", "Mozilla/5.0 (X11; Linux x86_64)")).toBe("google");
    expect(buildNavigationUrl(91, 8)).toBeNull();
    expect(buildNavigationUrl(49, -181)).toBeNull();
  });
});

describe("card", () => {
  beforeEach(() => { document.body.innerHTML = ""; });
  it("renders a controlled state for missing entity configuration", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ type: "custom:mobile-fuel-stations-card" }); await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("Overview-Entity auswählen"); });
  it("selects a deterministic overview stub and ignores foreign sensors", () => {
    const hass = { states: {
      "sensor.foreign_nearby_stations": state("2", { station_count: 2 }),
      "sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations": state("1", { station_count: 1, station_entities: [] }),
      "sensor.mobile_fuel_stations_device_tracker_auto_nearby_stations": state("1", { station_count: 1, location_entity: "device_tracker.auto" }),
    } };
    expect(MobileFuelStationsCard.getStubConfig(hass).entity).toBe("sensor.mobile_fuel_stations_device_tracker_auto_nearby_stations");
    expect(MobileFuelStationsCard.getStubConfig(hass, ["sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations"]).entity).toBe("sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations");
    expect(MobileFuelStationsCard.getStubConfig({ states: {} })).toEqual({ navigation: true });
  });
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
  it("keeps header metadata below the title on mobile", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); card.hass = hassFor(1, { radius: 20, fuel_type: "diesel" }); await card.updateComplete; expect(card.shadowRoot?.querySelector(".header h2")).toBeTruthy(); expect(card.shadowRoot?.querySelector(".header .summary")).toBeTruthy(); });
  it("shows navigation by default, can hide it, and keeps navigation separate from more-info", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); const hass = hassFor(1, {}, { latitude: 49, longitude: 8 }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".navigate")).toBeTruthy(); let moreInfo = false; card.addEventListener("hass-more-info", () => { moreInfo = true; }); (card.shadowRoot?.querySelector(".navigate") as HTMLElement).click(); expect(moreInfo).toBe(false);
    card.setConfig({ entity: overviewId, navigation: false }); await card.updateComplete; expect(card.shadowRoot?.querySelector(".navigate")).toBeNull();
    hass.states["sensor.vehicle_station_1"]!.attributes.latitude = 91; card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.querySelector(".navigate")).toBeNull();
  });
  it("renders English labels from the HA locale", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); const hass = hassFor(1, { fuel_type: "diesel" }) as ReturnType<typeof hassFor> & { locale?: { language: string } }; hass.locale = { language: "en" }; card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.textContent).toContain("Nearby fuel stations"); expect(card.shadowRoot?.textContent).toContain("Open"); });
  it("renders the configured navigation provider", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId, navigation_provider: "apple" }); card.hass = hassFor(1, {}, { latitude: 49, longitude: 8 }); await card.updateComplete;
    expect((card.shadowRoot?.querySelector(".navigate") as HTMLAnchorElement).href).toContain("maps.apple.com");
  });
  it("provides a visual editor that emits config-changed", async () => {
    expect(MobileFuelStationsCard.getConfigElement().localName).toBe("mobile-fuel-stations-card-editor");
    const editor = MobileFuelStationsCard.getConfigElement() as HTMLElement & { hass: unknown; setConfig: (config: unknown) => void; updateComplete: Promise<unknown> };
    document.body.append(editor); editor.hass = hassFor(1); editor.setConfig({ entity: overviewId, navigation: true }); await editor.updateComplete;
    let changed: CustomEvent | undefined; editor.addEventListener("config-changed", (event) => { changed = event as CustomEvent; });
    const select = editor.shadowRoot?.querySelector("select") as HTMLSelectElement; select.value = overviewId; select.dispatchEvent(new Event("change", { bubbles: true })); expect(changed?.detail.config.entity).toBe(overviewId);
    const checkbox = editor.shadowRoot?.querySelector("input[type=checkbox]") as HTMLInputElement; checkbox.checked = false; checkbox.dispatchEvent(new Event("change", { bubbles: true })); expect(changed?.detail.config.navigation).toBe(false);
    const provider = editor.shadowRoot?.querySelectorAll("select")[1] as HTMLSelectElement; expect(Array.from(provider.options).map((option) => option.value)).toEqual(["auto", "apple", "google", "waze"]); provider.value = "waze"; provider.dispatchEvent(new Event("change", { bubbles: true })); expect(changed?.detail.config.navigation_provider).toBe("waze"); expect(changed?.detail.config.entity).toBe(overviewId); expect(changed?.detail.config.navigation).toBe(false);
  });
  it("registers exactly one matching custom card suggestion", () => {
    const entry = window.customCards?.filter((card) => card.type === "mobile-fuel-stations-card");
    const suggestion = entry?.[0] as unknown as { getEntitySuggestion: (hass: unknown, entityId: string) => unknown };
    expect(entry).toHaveLength(1);
    expect(suggestion.getEntitySuggestion({ states: { [overviewId]: state("1", { station_entities: [] }) } }, overviewId)).toEqual({ config: { type: "custom:mobile-fuel-stations-card", entity: overviewId } });
    expect(suggestion.getEntitySuggestion({ states: { "sensor.foreign": state("1", { station_count: 1 }) } }, "sensor.foreign")).toBeNull();
  });
});
