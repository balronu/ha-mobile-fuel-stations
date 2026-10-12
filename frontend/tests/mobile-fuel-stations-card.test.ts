import { beforeEach, describe, expect, it } from "vitest";
import { buildBrandLogoUrl, buildNavigationUrl, detectNavigationProvider, discoverStationEntities, formatDistance, formatPrice, fuelLabel, MobileFuelStationsCard, normalizeLogoPath, resolveBrandLogoKey, shouldShowBrand } from "../src/mobile-fuel-stations-card";

const overviewId = "sensor.vehicle_nearby_stations";
const state = (value: string, attributes: Record<string, unknown> = {}) => ({ state: value, attributes });
const hassFor = (count: number, attrs: Record<string, unknown> = {}, stationAttrs: Record<string, unknown> = {}) => {
  const states: Record<string, ReturnType<typeof state>> = { [overviewId]: state("3", { station_count: count, station_entities: Array.from({ length: count }, (_, i) => `sensor.vehicle_station_${i + 1}`), ...attrs }) };
  for (let i = 1; i <= count; i++) states[`sensor.vehicle_station_${i}`] = state(String(1.5 + i / 100), { station_name: `Station ${i}`, distance: i, is_open: true, ...stationAttrs });
  return { states };
};

describe("formatting and discovery", () => {
  it("formats prices and distances with stable units", () => { expect(formatPrice("1.659")).toBe("1,659 €/l"); expect(formatDistance(1.25)).toBe("1,3 km"); expect(formatPrice(null)).toBeNull(); expect(formatDistance(null)).toBeNull(); });
  it("labels all selectable fuels, including HVO100", () => { expect(fuelLabel("e5")).toBe("E5"); expect(fuelLabel("E10")).toBe("E10"); expect(fuelLabel("diesel")).toBe("Diesel"); expect(fuelLabel("lpg")).toBe("LPG / Autogas"); expect(fuelLabel("hvo100")).toBe("HVO100"); });
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
  it("resolves supported brand aliases from the brand attribute only", () => {
    const aliases: Record<string, string> = {
      Aral: "aral", SHELL: "shell", "Esso ": "esso", "J.E.T.": "jet",
      Total: "total", TotalEnergies: "total", HEM: "hem", AVIA: "avia",
      "ORLEN Express": "orlen", OMV: "omv", "Q 1": "q1", Raiffeisen: "raiffeisen",
    };
    for (const [brand, key] of Object.entries(aliases)) expect(resolveBrandLogoKey(brand)).toBe(key);
    expect(resolveBrandLogoKey("Station Shell Nord")).toBeNull();
    expect(resolveBrandLogoKey("")).toBeNull();
    expect(resolveBrandLogoKey(undefined)).toBeNull();
  });
  it("builds only safe local logo URLs and rejects traversal or external paths", () => {
    expect(normalizeLogoPath("/local/fuel-logos/")).toBe("/local/fuel-logos/");
    expect(normalizeLogoPath("/hacsfiles/fuel-logos")).toBe("/hacsfiles/fuel-logos/");
    expect(normalizeLogoPath("https://evil.example/logos/")).toBeNull();
    expect(normalizeLogoPath("/local/../secret/")).toBeNull();
    expect(normalizeLogoPath("/local/fuel-logos/%0a/")).toBeNull();
    expect(buildBrandLogoUrl("Shell", "/local/fuel-logos/")).toBe("/local/fuel-logos/shell.png");
    expect(buildBrandLogoUrl("Shell", "https://evil.example/logos/")).toBeNull();
    expect(buildBrandLogoUrl("Unknown", "/local/fuel-logos/")).toBeNull();
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
  it("keeps logos disabled by default and renders safe user-owned logos when enabled", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId }); card.hass = hassFor(1, {}, { brand: "Shell", provider: "petromap" }); await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".station img")).toBeNull();
    card.setConfig({ entity: overviewId, show_brand_logos: true, logo_path: "/local/fuel-logos/" }); await card.updateComplete;
    const logo = card.shadowRoot?.querySelector(".station img") as HTMLImageElement;
    expect(logo?.src).toContain("/local/fuel-logos/shell.png");
    expect(logo?.alt).toContain("Station 1");
  });
  it("renders logos in nearest/cheapest highlights and falls back on image errors", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      nearest_station: { station_id: "nearest", station_name: "Nearest", brand: "ARAL", price: 1.7, distance: 1, latitude: 49, longitude: 8 },
      cheapest_station: { station_id: "cheapest", station_name: "Cheapest", brand: "JET", price: 1.6, distance: 2, latitude: 49, longitude: 8 },
    }, { brand: "Esso", station_id: "nearest", latitude: 49, longitude: 8 });
    card.setConfig({ entity: overviewId, show_brand_logos: true }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelectorAll(".highlight img")).toHaveLength(2);
    const logo = card.shadowRoot?.querySelector(".station img") as HTMLImageElement;
    logo.dispatchEvent(new Event("error")); await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".station img")).toBeNull();
    expect(card.shadowRoot?.querySelector(".station ha-icon")?.getAttribute("aria-label")).toBe("Unbekannte Tankstellenmarke");
  });
  it("renders stale data with an explicit warning and last-success time", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, { data_stale: true, last_successful_update: "2026-10-12T12:34:00+02:00", last_update_error_class: "ProviderTimeoutError" }, { price_stale: true });
    await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".stale-warning")?.textContent).toContain("Daten veraltet");
    expect(card.shadowRoot?.querySelector(".stale-warning")?.textContent).toContain("ProviderTimeoutError");
    expect(card.shadowRoot?.textContent).toContain("Daten veraltet");
    expect(card.shadowRoot?.textContent).toContain("Quelle unbekannt");
  });
  it("shows the actual provider for stations and highlights", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, { nearest_station: { station_id: "sensor-1", station_name: "Nearest", provider: "petromap", latitude: 49, longitude: 8 } }, { station_id: "sensor-1", provider: "tankerkoenig", latitude: 49, longitude: 8 });
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".summary")?.textContent).toContain("Quelle: Tankerkönig");
    expect(card.shadowRoot?.querySelector(".station .provider")?.textContent).toContain("Tankerkönig");
    expect(card.shadowRoot?.querySelector(".highlight .provider")?.textContent).toContain("Petromap");
  });
  it("marks mixed and missing provider metadata without guessing", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId });
    const hass = hassFor(2, {}, { provider: "tankerkoenig" });
    hass.states["sensor.vehicle_station_2"]!.attributes.provider = "petromap";
    card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".summary")?.textContent).toContain("Mehrere Datenquellen");
    hass.states["sensor.vehicle_station_1"]!.attributes.provider = undefined;
    hass.states["sensor.vehicle_station_2"]!.attributes.provider = undefined;
    card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".summary")?.textContent).toContain("Quelle unbekannt");
    expect(card.shadowRoot?.querySelector(".station .provider")?.textContent).toContain("Quelle unbekannt");
  });
  it("uses the card container instead of the window for responsive station layout", () => {
    const css = String((MobileFuelStationsCard as unknown as { styles: unknown }).styles);
    expect(css).toContain("container-type: inline-size");
    expect(css).toContain("@container (min-width: 600px)");
    expect(css).toContain(".stations { grid-template-columns: minmax(0, 1fr); }");
    expect(css).not.toContain(".stations { grid-template-columns: repeat(2");
  });
  it("keeps the logo slot bounded across supported responsive card widths", () => {
    const css = String((MobileFuelStationsCard as unknown as { styles: unknown }).styles);
    for (const width of [320, 375, 430, 600, 768, 1024]) expect(width).toBeGreaterThanOrEqual(320);
    expect(css).toContain(".brand-logo { width: 32px; height: 32px;");
    expect(css).toContain("object-fit: contain");
    expect(css).toContain("grid-template-columns: 32px minmax(0, 1fr) auto auto");
    expect(css).toContain("grid-template-columns: 26px minmax(0, 1fr) auto auto");
  });
  it("renders nearest and cheapest highlights from the overview", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      nearest_station: { station_id: "outside", station_name: "Nearest", brand: "ARAL", price: null, distance: 1.2, is_open: true, latitude: 49, longitude: 8 },
      cheapest_station: { station_id: "slot-1", station_name: "Cheapest", brand: "JET", price: 1.649, distance: 5.8, is_open: true, latitude: 49.1, longitude: 8.1 },
    }, { station_id: "slot-1", latitude: 49.1, longitude: 8.1 });
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelectorAll(".highlight")).toHaveLength(2);
    expect(card.shadowRoot?.textContent).toContain("Nächste");
    expect(card.shadowRoot?.textContent).toContain("Günstigste");
    expect(card.shadowRoot?.textContent).toContain("Preis nicht verfügbar");
    let entityId: string | undefined;
    card.addEventListener("hass-more-info", (event) => { entityId = (event as CustomEvent).detail.entityId; });
    (card.shadowRoot?.querySelectorAll(".highlight")[0] as HTMLElement).click();
    expect(entityId).toBeUndefined();
    (card.shadowRoot?.querySelectorAll(".highlight")[1] as HTMLElement).click();
    expect(entityId).toBe("sensor.vehicle_station_1");
    expect(card.shadowRoot?.querySelectorAll(".highlight .navigate")).toHaveLength(2);
  });
  it("merges nearest and per-fuel cheapest highlights for the same station", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      nearest_station: { station_id: "slot-1", station_name: "Compact Station", price: 1.799, distance: 1.2, latitude: 49, longitude: 8 },
      cheapest_stations_by_fuel: {
        diesel: { station_id: "slot-1", station_name: "Compact Station", fuel_type: "diesel", price: 1.799, distance: 1.2, latitude: 49, longitude: 8 },
        e10: { station_id: "slot-1", station_name: "Compact Station", fuel_type: "e10", price: 1.699, distance: 1.2, latitude: 49, longitude: 8 },
      },
    }, { station_id: "slot-1", latitude: 49, longitude: 8 });
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelectorAll(".highlight")).toHaveLength(1);
    expect(card.shadowRoot?.textContent).toContain("Nächste");
    expect(card.shadowRoot?.textContent).toContain("Günstigste Diesel");
    expect(card.shadowRoot?.textContent).toContain("Günstigste E10");
    expect(card.shadowRoot?.querySelectorAll(".highlight .navigate")).toHaveLength(1);
  });
  it("wraps long station details without losing prices or navigation", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {}, {
      station_name: "Sehr lange Tankstellenbezeichnung mit Ortszusatz und Zusatzinformationen",
      street: "Eine außergewöhnlich lange Straßenbezeichnung", house_number: "123456789", postcode: "12345", place: "Eine sehr lange Ortsbezeichnung",
      latitude: 49, longitude: 8, fuel_prices: { diesel: 1.799, e10: null },
    });
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    const station = card.shadowRoot?.querySelector(".station");
    expect(station?.textContent).toContain("Sehr lange Tankstellenbezeichnung");
    expect(station?.textContent).toContain("Preis nicht verfügbar");
    expect(station?.querySelector(".navigate")).toBeTruthy();
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
  it("recovers from unavailable without remounting and survives a remount", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId });
    card.hass = { states: { [overviewId]: state("unavailable") } }; await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("nicht verfügbar");
    card.hass = hassFor(1); await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Station 1");
    card.remove(); document.body.append(card); card.hass = hassFor(1); await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Station 1");
  });
  it("dispatches more-info with the station entity id", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); card.hass = hassFor(1); await card.updateComplete; let event: Event | undefined; card.addEventListener("hass-more-info", (value) => { event = value; }); (card.shadowRoot?.querySelector(".station") as HTMLElement).click(); expect((event as CustomEvent).detail.entityId).toBe("sensor.vehicle_station_1"); });
  it("keeps header metadata below the title on mobile", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); card.hass = hassFor(1, { radius: 20, fuel_type: "diesel" }); await card.updateComplete; expect(card.shadowRoot?.querySelector(".header h2")).toBeTruthy(); expect(card.shadowRoot?.querySelector(".header .summary")).toBeTruthy(); });
  it("renders multiple selected fuels and station fuel metadata", async () => { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId }); const hass = hassFor(1, { fuel_types: ["diesel", "hvo100"] }, { fuel_type: "hvo100", requested_fuel: "hvo100" }); card.hass = hass; await card.updateComplete; expect(card.shadowRoot?.querySelector(".summary")?.textContent).toContain("Diesel, HVO100"); expect(card.shadowRoot?.textContent).toContain("HVO100"); });
  it("shows Nakordoni attribution only for Nakordoni data", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, { provider: "nakordoni" }); await card.updateComplete;
    const attribution = card.shadowRoot?.querySelector("a[href='https://nakordoni.eu']") as HTMLAnchorElement;
    expect(attribution?.textContent).toBe("Data by nakordoni.eu"); expect(attribution?.target).toBe("_blank");
    card.hass = hassFor(1, { provider: "tankerkoenig" }); await card.updateComplete;
    expect(card.shadowRoot?.querySelector("a[href='https://nakordoni.eu']")).toBeNull();
  });
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
