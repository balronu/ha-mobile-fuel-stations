import { beforeEach, describe, expect, it, vi } from "vitest";
import { buildBrandLogoUrl, buildNavigationUrl, detectNavigationProvider, discoverStationEntities, findOverviewEntity, formatDistance, formatPrice, fuelLabel, isOverviewEntity, MobileFuelStationsCard, normalizeLogoPath, resolveBrandLogoKey, shouldShowBrand } from "../src/mobile-fuel-stations-card";

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
  it("resolves supported brand aliases from brand and station name", () => {
    const aliases: Record<string, string> = {
      Aral: "aral", SHELL: "shell", "Esso ": "esso", "J.E.T.": "jet",
      Total: "total", TotalEnergies: "total", HEM: "hem", AVIA: "avia",
      "ORLEN Express": "orlen", OMV: "omv", "Q 1": "q1", Raiffeisen: "raiffeisen",
    };
    for (const [brand, key] of Object.entries(aliases)) expect(resolveBrandLogoKey(brand)).toBe(key);
    expect(resolveBrandLogoKey("Station Shell Nord")).toBe("shell");
    expect(resolveBrandLogoKey("Aral Tankstelle")).toBe("aral");
    expect(resolveBrandLogoKey(null, "Aral Tankstelle am Bahnhof")).toBe("aral");
    expect(resolveBrandLogoKey(null, "Total Energies Station")).toBe("total");
    expect(resolveBrandLogoKey(null, "Unabhängige Tankstelle")).toBeNull();
    expect(resolveBrandLogoKey("")).toBeNull();
    expect(resolveBrandLogoKey(undefined)).toBeNull();
  });
  it("recognizes every named reference inventory entry with canonical local assets", () => {
    const referenceAliases: Record<string, string> = {
      Access: "access", Allguth: "allguth", "Bell Oil": "bell-oil", Calpam: "calpam",
      "citi oil SB-Tankstelle": "citi-oil-sb-tankstelle", "E-Center": "e-center", ELAN: "elan",
      Feneberg: "feneberg", "Fläming Tank": "flaeming-tank", Greenline: "greenline", Grüne: "gruene",
      Hessol: "hessol", Hornbach: "hornbach", "Jantzon Tankstelle": "aral", Joiss: "joiss",
      "K+K Klaas & Kock": "kk-klaas-kock", "Minera Automatenstation": "minera", Minera: "minera",
      "Mr. Wash Autoservice AG": "mr-wash-autoservice-ag", MTB: "mtb", "Mundorf Tank": "mundorf-tank",
      Nordoel: "nordoel", Oktan: "oktan", PIN: "pin", RAN: "ran", "Roth Energie": "roth-energie", SB: "sb",
      Schillhorn: "schillhorn-tankstelle", Schindele: "schindele", SCORE: "score", Spreves: "spreves",
      "Supermarkt-Tankstelle": "supermarkt-tankstelle", Trigema: "trigema", "V-Markt": "v-markt",
    };
    for (const [brand, key] of Object.entries(referenceAliases)) expect(resolveBrandLogoKey(brand)).toBe(key);
    for (const brand of Object.keys(referenceAliases)) {
      if (!buildBrandLogoUrl(brand)) throw new Error("missing logo for " + brand);
    }
    expect(buildBrandLogoUrl("GULF")).toBe("/mobile_fuel_stations/logos/gulf.png");
    expect(buildBrandLogoUrl("TinQ")).toBe("/mobile_fuel_stations/logos/tinq.png");
  });
  it("resolves the reported provider names from station names and invalidates old bundle caches", () => {
    expect(resolveBrandLogoKey(null, "Eni (Agip Eni)")).toBe("agip-eni");
    expect(buildBrandLogoUrl(null, undefined, "Eni (Agip Eni)")).toBe("/mobile_fuel_stations/logos/agip-eni.png");
    expect(resolveBrandLogoKey(null, "OIL! Tankstelle Sulzbach")).toBe("oil");
    expect(buildBrandLogoUrl(null, undefined, "OIL! Tankstelle Sulzbach")).toBe("/mobile_fuel_stations/logos/oil.png");
  });
  it("maps every bundled logo key to a local resource path", () => {
    const bundled = [
      ["Aral", "aral.png"], ["JET", "jet.png"], ["OMV", "omv.png"], ["ORLEN", "orlen.png"],
      ["Shell", "shell.png"], ["TotalEnergies", "total.png"], ["Access", "access.png"],
      ["Agip Eni", "agip-eni.png"], ["Allguth", "allguth.png"], ["Avia Xpress", "avia-xpress.png"],
      ["Avia", "avia.png"], ["BayWa", "baywa.png"], ["Bell Oil", "bell-oil.png"], ["bft", "bft.png"],
      ["Calpam", "calpam.png"], ["citi oil SB-Tankstelle", "citi-oil-sb-tankstelle.png"],
      ["CLASSIC", "classic.png"], ["E-Center", "e-center.png"], ["ED", "ed.png"], ["EDEKA", "edeka.png"],
      ["ELAN", "elan.png"], ["Esso", "esso.png"], ["Feneberg", "feneberg.png"],
      ["Fläming Tank", "flaeming-tank.png"], ["Globus", "globus.png"], ["Greenline", "greenline.png"],
      ["Grüne", "gruene.png"], ["Gulf", "gulf.png"], ["HEM", "hem.png"], ["Hessol", "hessol.png"],
      ["Hornbach", "hornbach.png"], ["Hoyer", "hoyer.png"], ["Joiss", "joiss.png"],
      ["K+K Klaas & Kock", "kk-klaas-kock.png"], ["Minera", "minera.png"], ["MOL", "mol.png"],
      ["Mr. Wash Autoservice AG", "mr-wash-autoservice-ag.png"], ["MTB", "mtb.png"],
      ["Mundorf Tank", "mundorf-tank.png"], ["Nordoel", "nordoel.png"], ["OIL!", "oil.png"],
      ["Oktan", "oktan.png"], ["PIN", "pin.png"], ["Q1", "q1.png"], ["Raiffeisen", "raiffeisen.png"],
      ["RAN", "ran.png"], ["Roth Energie", "roth-energie.png"], ["SB", "sb.png"],
      ["Schillhorn", "schillhorn-tankstelle.png"], ["Schindele", "schindele.png"],
      ["SCORE", "score.png"], ["Spreves", "spreves.png"], ["Sprint", "sprint.png"], ["star", "star.png"],
      ["Supermarkt-Tankstelle", "supermarkt-tankstelle.png"], ["team", "team.png"], ["TinQ", "tinq.png"],
      ["Trigema", "trigema.png"], ["V-Markt", "v-markt.png"], ["Westfalen", "westfalen.png"],
    ] as const;
    for (const [brand, filename] of bundled) {
      expect(buildBrandLogoUrl(brand), brand).toBe("/mobile_fuel_stations/logos/" + filename);
    }
    expect(bundled).toHaveLength(60);
  });
  it("covers all 62 named reference stems while keeping the 404 entry non-brand", () => {
    const referenceStems = [
      "access", "agip-eni", "allguth", "aral", "avia-xpress", "avia", "baywa", "bell-oil", "bft", "calpam",
      "citi-oil-sb-tankstelle", "classic", "e-center", "ed", "edeka", "elan", "esso", "feneberg", "flaeming-tank",
      "globus", "greenline", "gruene", "hem", "hessol", "hornbach", "hoyer", "jantzon-tankstelle", "jet", "joiss",
      "kk-klaas--kock", "minera-automatenstation", "minera", "mol", "mr-wash-autoservice-ag", "mtb", "mundorf-tank",
      "nordoel", "oil", "oktan", "omv", "orlen", "pin", "q1", "raiffeisen", "ran", "roth-energie", "sb",
      "schillhorn-tankstelle", "schindele", "score", "shell", "spreves", "sprint", "star", "supermarkt-tankstelle",
      "svg", "team", "total", "totalenergies", "trigema", "v-markt", "westfalen",
    ];
    expect(referenceStems).toHaveLength(62);
    for (const stem of referenceStems) expect(resolveBrandLogoKey(stem), stem).not.toBeNull();
    expect(resolveBrandLogoKey("404")).toBeNull();
  });
  it("builds only safe local logo URLs and rejects traversal or external paths", () => {
    expect(normalizeLogoPath("/local/fuel-logos/")).toBe("/local/fuel-logos/");
    expect(normalizeLogoPath("/hacsfiles/fuel-logos")).toBe("/hacsfiles/fuel-logos/");
    expect(normalizeLogoPath("https://evil.example/logos/")).toBeNull();
    expect(normalizeLogoPath("/local/../secret/")).toBeNull();
    expect(normalizeLogoPath("/local/fuel-logos/%0a/")).toBeNull();
    expect(buildBrandLogoUrl("Shell", "/local/fuel-logos/")).toBe("/local/fuel-logos/shell.png");
    expect(buildBrandLogoUrl("Shell")).toBe("/mobile_fuel_stations/logos/shell.png");
    expect(buildBrandLogoUrl(null, undefined, "Aral Tankstelle")).toBe("/mobile_fuel_stations/logos/aral.png");
    expect(buildBrandLogoUrl("Esso")).toBe("/mobile_fuel_stations/logos/esso.png");
    expect(buildBrandLogoUrl("Shell", "https://evil.example/logos/")).toBeNull();
    expect(buildBrandLogoUrl("Unknown", "/local/fuel-logos/")).toBeNull();
  });
  it("keeps short or ambiguous aliases exact and rejects substring matches", () => {
    for (const [brand, key] of [["ED", "ed"], ["SB", "sb"], ["OIL", "oil"], ["PIN", "pin"], ["Q1", "q1"], ["SVG", "svg"]]) {
      expect(resolveBrandLogoKey(brand)).toBe(key);
    }
    for (const brand of ["ED Station", "SB24", "OILFIELD", "PINK", "Q10", "SVGStation", "Aralissimo"]) {
      expect(resolveBrandLogoKey(brand)).toBeNull();
      expect(buildBrandLogoUrl(brand, "/local/fuel-logos/")).toBeNull();
    }
    expect(resolveBrandLogoKey(null, "ED Station Nord")).toBeNull();
    expect(resolveBrandLogoKey(null, "Q10 Tankstelle")).toBeNull();
    expect(resolveBrandLogoKey(null, "Aral Tankstelle Nord")).toBe("aral");
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
    expect(MobileFuelStationsCard.getStubConfig({ states: {} })).toEqual({ navigation: true, display_mode: "compact" });
  });
  it("discovers multiple integration entries even when one is unavailable", () => {
    const grandland = "sensor.mobile_fuel_stations_device_tracker_auto_grandland_fahrzeug_nearby_stations";
    const wohnmobil = "sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations";
    const hass = { states: {
      [grandland]: state("unavailable", { friendly_name: "Opel Grandland" }),
      [wohnmobil]: state("5", { station_count: 5, station_entities: [] }),
    } };
    expect(isOverviewEntity(grandland, hass.states[grandland])).toBe(true);
    expect(findOverviewEntity(hass)).toBe(grandland);
    expect(MobileFuelStationsCard.getStubConfig(hass).entity).toBe(grandland);
  });
  it("renders overview, one, five and ten stations in order", async () => {
    for (const count of [1, 5, 10]) { const card = new MobileFuelStationsCard(); document.body.append(card); card.setConfig({ type: "custom:mobile-fuel-stations-card", entity: overviewId }); card.hass = hassFor(count); await card.updateComplete; expect(card.shadowRoot?.querySelectorAll(".station")).toHaveLength(count); expect(card.shadowRoot?.textContent).toContain("Station 1"); }
  });
  it("shows the manual fetch control and calls only the selected entry service", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn().mockResolvedValue(undefined);
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "manual" }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Abrufmodus");
    expect(card.shadowRoot?.textContent).toContain("Jetzt abrufen");
    (card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement)?.click();
    expect(callService).toHaveBeenCalledWith("mobile_fuel_stations", "manual_refresh", { entry_id: "entry-opel" });
  });
  it("disables manual refresh from the backend cooldown and re-enables after backend expiry", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn().mockResolvedValue(undefined);
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "manual", provider_cooldown_remaining: 157, last_update_result: "provider_cooldown" }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    const refresh = card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement;
    expect(refresh.disabled).toBe(true);
    expect(refresh.textContent).toContain("Erneut abrufen in");
    refresh.click();
    expect(callService).not.toHaveBeenCalled();
    hass.states[overviewId]!.attributes.provider_cooldown_remaining = 0;
    hass.states[overviewId]!.attributes.last_update_result = "provider_success";
    card.hass = hass; await card.updateComplete;
    expect((card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement).disabled).toBe(false);
  });
  it("keeps manual refresh enabled when a permitted fallback provider is available", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn().mockResolvedValue(undefined);
    const hass = { ...hassFor(1, {
      config_entry_id: "entry-womo",
      fetch_mode: "manual",
      manual_refresh_available: true,
      provider_cooldown_remaining: 240,
      manual_refresh_retry_seconds: 0,
      provider_cooldowns: {
        tankerkoenig: { active: true, cooldown_until: new Date(Date.now() + 240000).toISOString(), remaining_seconds: 240 },
        nakordoni: { active: false, cooldown_until: null, remaining_seconds: 0 },
      },
      provider_quotas: {
        tankerkoenig: { available: false },
        nakordoni: { available: false },
      },
    }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect((card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement).disabled).toBe(false);
    expect(card.shadowRoot?.querySelector("button.refresh")?.textContent).toContain("Jetzt abrufen");
    expect(card.shadowRoot?.textContent).toContain("Tankerkönig");
    expect(card.shadowRoot?.textContent).toContain("Provider-Cooldown aktiv");
  });
  it("does not show a global cooldown when the backend says no retry can unlock a provider", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn();
    const hass = { ...hassFor(1, {
      config_entry_id: "entry-womo",
      fetch_mode: "manual",
      manual_refresh_available: false,
      provider_cooldown_remaining: 240,
      manual_refresh_retry_seconds: 0,
      provider_availability: {
        tankerkoenig: { available: false, status: "cooldown" },
        nakordoni: { available: false, status: "coverage_unknown" },
      },
      provider_cooldowns: {
        tankerkoenig: { active: true, cooldown_until: new Date(Date.now() + 240000).toISOString(), remaining_seconds: 240 },
        nakordoni: { active: false, cooldown_until: null, remaining_seconds: 0 },
      },
    }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    const refresh = card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement;
    expect(refresh.disabled).toBe(true);
    expect(refresh.textContent).not.toContain("Erneut abrufen in");
    expect(refresh.textContent).toContain("Kein Provider verfügbar");
  });
  it("renders verified quota data and marks unsupported provider quotas unavailable", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      provider_cooldowns: { nakordoni: { active: false, cooldown_until: null, remaining_seconds: 0 } },
      provider_quotas: {
        nakordoni: { available: true, stale: false, quotas: { cheap: { remaining: 7, limit: 10 } } },
        tankerkoenig: { available: false },
      },
    });
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("7/10 Aufrufe verbleibend");
    expect(card.shadowRoot?.textContent).toContain("Tankerkönig · Kontingent nicht verfügbar");
  });
  it("renders the backend provider reason instead of a misleading quota state", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      provider_availability: {
        tankerkoenig: { available: false, status: "cooldown" },
        nakordoni: { available: false, status: "coverage_unknown" },
      },
      provider_cooldowns: { tankerkoenig: { active: false, remaining_seconds: 0 }, nakordoni: { active: false, remaining_seconds: 0 } },
      provider_quotas: { tankerkoenig: { available: false }, nakordoni: { available: false } },
    });
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Nakordoni · Marktabdeckung unbekannt");
  });
  it("shows a country diagnostic instead of a generic provider message", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn();
    const hass = { ...hassFor(1, {
      config_entry_id: "entry-womo",
      fetch_mode: "manual",
      manual_refresh_available: false,
      manual_refresh_retry_seconds: 0,
      manual_refresh_blocked_reason: "nakordoni:country_unknown;tankerkoenig:country_unknown",
      provider_availability: {
        tankerkoenig: { available: false, status: "country_unknown" },
        nakordoni: { available: false, status: "country_unknown" },
      },
    }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    const refresh = card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement;
    expect(refresh.disabled).toBe(true);
    expect(refresh.textContent).toContain("Land nicht bestätigt");
    expect(card.shadowRoot?.textContent).toContain("Tankerkönig · Land nicht bestätigt");
  });
  it("keeps the button enabled when Tankerkönig is available and Nakordoni coverage is unknown", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn();
    const hass = { ...hassFor(1, {
      config_entry_id: "entry-womo",
      fetch_mode: "manual",
      manual_refresh_available: true,
      manual_refresh_retry_seconds: 0,
      provider_cooldown_remaining: 0,
      provider_availability: {
        tankerkoenig: { available: true, status: "available" },
        nakordoni: { available: false, status: "coverage_unknown" },
      },
    }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    const refresh = card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement;
    expect(refresh.disabled).toBe(false);
    expect(refresh.textContent).toContain("Jetzt abrufen");
    expect(card.shadowRoot?.textContent).toContain("Nakordoni · Marktabdeckung unbekannt");
  });
  it("keeps the confirmed backend mode while a mode change is pending", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    let resolveService: (() => void) | undefined;
    const callService = vi.fn().mockImplementation(() => new Promise<void>((resolve) => { resolveService = resolve; }));
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "automatic" }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    (card.shadowRoot?.querySelectorAll(".mode-switch button")[1] as HTMLButtonElement).click();
    await card.updateComplete;
    expect((card.shadowRoot?.querySelector(".mode-switch button.selected") as HTMLButtonElement).textContent).toContain("Automatisch");
    expect(card.shadowRoot?.textContent).toContain("Station 1");
    resolveService?.(); await Promise.resolve(); await card.updateComplete;
    expect((card.shadowRoot?.querySelector(".mode-switch button.selected") as HTMLButtonElement).textContent).toContain("Automatisch");
    hass.states[overviewId]!.attributes.fetch_mode = "manual";
    card.hass = hass; await card.updateComplete;
    expect((card.shadowRoot?.querySelector(".mode-switch button.selected") as HTMLButtonElement).textContent).toContain("Manuell");
  });
  it("shows a mode error without replacing existing station data", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn().mockRejectedValue(new Error("name 'hass' is not defined"));
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "automatic" }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    (card.shadowRoot?.querySelectorAll(".mode-switch button")[1] as HTMLButtonElement).click();
    await Promise.resolve(); await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("name 'hass' is not defined");
    expect(card.shadowRoot?.textContent).toContain("Station 1");
    expect((card.shadowRoot?.querySelector(".mode-switch button.selected") as HTMLButtonElement).textContent).toContain("Automatisch");
    expect(card.shadowRoot?.querySelector(".stations")).toBeTruthy();
  });
  it("keeps station data visible when manual refresh fails and clears the error after success", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn()
      .mockRejectedValueOnce(new Error("Manual refresh failed"))
      .mockResolvedValueOnce(undefined);
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "manual" }), callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    (card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement).click();
    await Promise.resolve(); await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Manual refresh failed");
    expect(card.shadowRoot?.textContent).toContain("Station 1");
    (card.shadowRoot?.querySelector("button.refresh") as HTMLButtonElement).click();
    await Promise.resolve(); await card.updateComplete;
    expect(card.shadowRoot?.textContent).not.toContain("Manual refresh failed");
    expect(card.shadowRoot?.textContent).toContain("Station 1");
  });
  it("does not mark a fresh manual result stale solely because the mode is manual", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, { fetch_mode: "manual", data_stale: false, last_successful_update: new Date().toISOString() });
    await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".stale-warning")).toBeNull();
    expect(card.shadowRoot?.textContent).toContain("Station 1");
  });
  it("keeps multiple cards for one config entry on the confirmed backend mode", async () => {
    const first = new MobileFuelStationsCard(); const second = new MobileFuelStationsCard(); document.body.append(first, second);
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "manual" }), callService: vi.fn().mockResolvedValue(undefined) };
    first.setConfig({ entity: overviewId }); second.setConfig({ entity: overviewId }); first.hass = hass; second.hass = hass;
    await first.updateComplete; await second.updateComplete;
    expect(first.shadowRoot?.querySelector(".mode-switch button.selected")?.textContent).toContain("Manuell");
    expect(second.shadowRoot?.querySelector(".mode-switch button.selected")?.textContent).toContain("Manuell");
  });
  it("keeps the card read-only for a non-admin dashboard user", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn().mockResolvedValue(undefined);
    const hass = { ...hassFor(1, { config_entry_id: "entry-opel", fetch_mode: "manual" }), user: { is_admin: false }, callService };
    card.setConfig({ entity: overviewId }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".controls")).toBeNull();
    expect(card.shadowRoot?.textContent).toContain("Station 1");
    expect(callService).not.toHaveBeenCalled();
  });
  it("shows logos by default and respects an explicit opt-out", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId }); card.hass = hassFor(1, {}, { brand: "Shell", provider: "petromap" }); await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".station img")?.getAttribute("src")).toContain("/mobile_fuel_stations/logos/shell.png");
    card.setConfig({ entity: overviewId, show_brand_logos: false, logo_path: "/local/fuel-logos/" }); await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".station img")).toBeNull();
    card.setConfig({ entity: overviewId, logo_path: "/local/fuel-logos/" }); await card.updateComplete;
    const logo = card.shadowRoot?.querySelector(".station img") as HTMLImageElement;
    expect(logo?.src).toContain("/local/fuel-logos/shell.png");
    expect(logo?.alt).toContain("Station 1");
  });
  it("uses the station name when the provider leaves brand empty", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, {}, { station_name: "Aral Tankstelle am Bahnhof", brand: "" });
    await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".station img")?.getAttribute("src")).toContain("/mobile_fuel_stations/logos/aral.png");
  });
  it("renders logos in nearest/cheapest highlights and falls back on image errors", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      nearest_station: { station_id: "nearest", station_name: "Nearest", brand: "ARAL", price: 1.7, distance: 1, latitude: 49, longitude: 8 },
      cheapest_station: { station_id: "cheapest", station_name: "Cheapest", brand: "JET", price: 1.6, distance: 2, latitude: 49, longitude: 8 },
    }, { brand: "ARAL", station_id: "nearest", latitude: 49, longitude: 8 });
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
  it("distinguishes stale provider prices from a stale API result", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, { data_stale: false, last_update_result: "provider_success", last_successful_update: new Date().toISOString() }, { price_stale: true });
    await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Providerpreise sind veraltet");
    expect(card.shadowRoot?.querySelector(".stale-warning")?.textContent).not.toContain("Daten veraltet");
  });
  it("renders distinct location, response, quota, and network errors", async () => {
    for (const [result, label] of [["gps_unavailable", "Standortdaten fehlen"], ["provider_response_error", "Provider-Antwort konnte nicht verarbeitet werden"], ["provider_quota_exhausted", "API-Kontingent erschöpft"], ["network_timeout", "Netzwerk-/Timeout-Fehler beim Provider"]] as const) {
      const card = new MobileFuelStationsCard(); document.body.append(card);
      card.setConfig({ entity: overviewId });
      card.hass = hassFor(1, { last_update_result: result, data_stale: false });
      await card.updateComplete;
      expect(card.shadowRoot?.textContent).toContain(label);
      card.remove();
    }
  });
  it("shows a successful fallback provider without hiding station data", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, {
      last_update_result: "provider_success",
      fallback_attempted: true,
      fallback_provider: "nakordoni",
      fallback_result: "success",
    });
    await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Ersatzanbieter verwendet: Nakordoni");
    expect(card.shadowRoot?.querySelectorAll(".station")).toHaveLength(1);
    card.remove();
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
    expect(css).toContain("grid-template-columns: 36px minmax(0, 1fr) minmax(92px, auto) 36px");
    expect(css).toContain("@container (max-width: 360px)");
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
  it("uses compact mode without duplicate highlight cards and marks nearest/cheapest inline", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {
      nearest_station: { station_id: "slot-1", station_name: "Compact Station", latitude: 49, longitude: 8 },
      cheapest_stations_by_fuel: { diesel: { station_id: "slot-1", station_name: "Compact Station", fuel_type: "diesel", price: 1.699, latitude: 49, longitude: 8 } },
      provider_quotas: { tankerkoenig: { available: true, quotas: { cheap: { remaining: 8, limit: 10 } } } },
    }, { station_id: "slot-1", fuel_prices: { diesel: 1.699 }, latitude: 49, longitude: 8 });
    card.setConfig({ entity: overviewId, display_mode: "compact" }); card.hass = hass; await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".highlight")).toBeNull();
    expect(card.shadowRoot?.querySelectorAll(".station-badge")).toHaveLength(2);
    expect(card.shadowRoot?.querySelector(".diagnostics")).toBeTruthy();
    expect(card.shadowRoot?.textContent).toContain("8/10 Aufrufe verbleibend");
  });
  it("keeps multiple fuel prices side by side in compact mode and preserves missing prices", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId, display_mode: "compact" });
    card.hass = hassFor(1, { fuel_types: ["e10", "diesel"] }, { fuel_prices: { e10: 1.659, diesel: null }, latitude: 49, longitude: 8 });
    await card.updateComplete;
    expect(card.shadowRoot?.querySelectorAll(".fuel-price")).toHaveLength(2);
    expect(card.shadowRoot?.textContent).toContain("E10");
    expect(card.shadowRoot?.textContent).toContain("Diesel");
    expect(card.shadowRoot?.textContent).toContain("Preis nicht verfügbar");
  });
  it("renders every compact station as one dense row with inline metadata", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(5, {
      nearest_station: { station_id: "slot-2", station_name: "Nearest", latitude: 49, longitude: 8 },
      cheapest_stations_by_fuel: { diesel: { station_id: "slot-2", station_name: "Nearest", fuel_type: "diesel", price: 1.699, latitude: 49, longitude: 8 } },
    }, { station_id: "slot-2", street: "Hauptstraße", house_number: "1", postcode: "66111", place: "Saarbrücken", distance: 2.4, is_open: false, latitude: 49, longitude: 8, fuel_prices: { e10: 1.659, diesel: 1.699 } });
    card.setConfig({ entity: overviewId, display_mode: "compact" }); card.hass = hass; await card.updateComplete;
    const rows = [...(card.shadowRoot?.querySelectorAll(".compact-station") ?? [])];
    expect(rows).toHaveLength(5);
    expect(rows.every((row) => row.querySelector(".station-main .name") && row.querySelector(".station-main .address") && row.querySelector(".station-meta"))).toBe(true);
    expect(rows.every((row) => !row.querySelector(".provider"))).toBe(true);
    expect(rows.every((row) => row.querySelectorAll(".navigate").length === 1)).toBe(true);
    expect(rows[1].querySelector(".station-meta")?.textContent).toContain("Geschlossen");
    expect(rows[1].querySelector(".station-meta")?.textContent).toContain("2,4 km");
    expect(rows[1].querySelectorAll(".fuel-price")).toHaveLength(2);
    expect(rows[1].querySelectorAll(".station-badge")).toHaveLength(2);
    expect(card.shadowRoot?.querySelectorAll(".highlight")).toHaveLength(0);
  });
  it("keeps compact names and addresses bounded while preserving keyboard navigation", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const hass = hassFor(1, {}, { station_name: "Eine außergewöhnlich lange Tankstellenbezeichnung mit vielen Ortszusätzen", street: "Eine sehr lange Straße", house_number: "123456789", postcode: "12345", place: "Ein sehr langer Ort", distance: 1.1, latitude: 49, longitude: 8 });
    card.setConfig({ entity: overviewId, display_mode: "compact" }); card.hass = hass; await card.updateComplete;
    const row = card.shadowRoot?.querySelector(".compact-station") as HTMLElement;
    expect(row.querySelector(".name")?.getAttribute("title")).toContain("außergewöhnlich lange");
    expect(row.querySelector(".address")?.getAttribute("title")).toContain("sehr lange Straße");
    const css = String((MobileFuelStationsCard as unknown as { styles: unknown }).styles);
    expect(css).toContain("text-overflow: ellipsis; white-space: nowrap");
    expect(row.querySelector(".navigate")).toBeTruthy();
    let entityId: string | undefined;
    card.addEventListener("hass-more-info", (event) => { entityId = (event as CustomEvent).detail.entityId; });
    row.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    expect(entityId).toBe("sensor.vehicle_station_1");
  });
  it("does not make provider calls while rendering compact rows", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    const callService = vi.fn();
    const hass = { ...hassFor(5), callService };
    card.setConfig({ entity: overviewId, display_mode: "compact" }); card.hass = hass; await card.updateComplete;
    expect(callService).not.toHaveBeenCalled();
    expect(card.shadowRoot?.querySelectorAll(".compact-station")).toHaveLength(5);
  });
  it("keeps legacy YAML cards in detailed mode while new stubs are compact", async () => {
    const card = new MobileFuelStationsCard(); document.body.append(card);
    card.setConfig({ entity: overviewId });
    card.hass = hassFor(1, { nearest_station: { station_id: "slot-1", station_name: "Nearest", latitude: 49, longitude: 8 } }, { station_id: "slot-1", latitude: 49, longitude: 8 });
    await card.updateComplete;
    expect(card.shadowRoot?.querySelector(".detailed-mode")).toBeTruthy();
    expect(card.shadowRoot?.querySelector(".highlight")).toBeTruthy();
    expect(MobileFuelStationsCard.getStubConfig(hassFor(1)).display_mode).toBe("compact");
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
    const mode = editor.shadowRoot?.querySelectorAll("select")[0] as HTMLSelectElement; expect(Array.from(mode.options).map((option) => option.value)).toEqual(["compact", "detailed"]); mode.value = "compact"; mode.dispatchEvent(new Event("change", { bubbles: true })); expect(changed?.detail.config.display_mode).toBe("compact");
    const checkbox = editor.shadowRoot?.querySelector("input[type=checkbox]") as HTMLInputElement; checkbox.checked = false; checkbox.dispatchEvent(new Event("change", { bubbles: true })); expect(changed?.detail.config.navigation).toBe(false);
    const provider = editor.shadowRoot?.querySelectorAll("select")[2] as HTMLSelectElement; expect(Array.from(provider.options).map((option) => option.value)).toEqual(["auto", "apple", "google", "waze"]); provider.value = "waze"; provider.dispatchEvent(new Event("change", { bubbles: true })); expect(changed?.detail.config.navigation_provider).toBe("waze"); expect(changed?.detail.config.entity).toBe(overviewId); expect(changed?.detail.config.navigation).toBe(false);
  });
  it("lists unavailable overview entities from separate vehicle entries", async () => {
    const editor = MobileFuelStationsCard.getConfigElement() as HTMLElement & { hass: unknown; setConfig: (config: unknown) => void; updateComplete: Promise<unknown> };
    document.body.append(editor);
    editor.hass = { states: {
      "sensor.mobile_fuel_stations_device_tracker_auto_grandland_fahrzeug_nearby_stations": state("unavailable", { friendly_name: "Opel Grandland" }),
      "sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations": state("5", { station_count: 5, station_entities: [] }),
    } };
    editor.setConfig({ entity: "sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations" });
    await editor.updateComplete;
    const select = editor.shadowRoot?.querySelectorAll("select")[1] as HTMLSelectElement;
    expect(Array.from(select.options).map((option) => option.value)).toEqual([
      "",
      "sensor.mobile_fuel_stations_device_tracker_auto_grandland_fahrzeug_nearby_stations",
      "sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations",
    ]);
  });
  it("keeps direct YAML entity configuration compatible while unavailable", async () => {
    const card = new MobileFuelStationsCard();
    document.body.append(card);
    card.setConfig({ entity: "sensor.mobile_fuel_stations_device_tracker_auto_grandland_fahrzeug_nearby_stations" });
    card.hass = { states: { "sensor.mobile_fuel_stations_device_tracker_auto_grandland_fahrzeug_nearby_stations": state("unavailable") } };
    await card.updateComplete;
    expect(card.shadowRoot?.textContent).toContain("Tankstellen derzeit nicht verfügbar");
  });
  it("registers exactly one matching custom card suggestion", () => {
    const entry = window.customCards?.filter((card) => card.type === "mobile-fuel-stations-card");
    const suggestion = entry?.[0] as unknown as { getEntitySuggestion: (hass: unknown, entityId: string) => unknown };
    expect(entry).toHaveLength(1);
    expect(suggestion.getEntitySuggestion({ states: { [overviewId]: state("1", { station_entities: [] }) } }, overviewId)).toEqual({ config: { type: "custom:mobile-fuel-stations-card", entity: overviewId } });
    expect(suggestion.getEntitySuggestion({ states: { "sensor.foreign": state("1", { station_count: 1 }) } }, "sensor.foreign")).toBeNull();
  });
});
