import { LitElement, css, html, nothing } from "lit";

export const FRONTEND_BUILD_VERSION = "0.8.4-beta.4";

type HassState = {
  state: string;
  attributes: Record<string, unknown>;
};

type Hass = {
  states: Record<string, HassState | undefined>;
  user?: { is_admin?: boolean };
  locale?: { language?: string };
  callService?: (domain: string, service: string, data: Record<string, unknown>) => Promise<unknown>;
};

export type StationRow = { id: string; state: HassState };
export type StationPriority = StationRow & { isNearest: boolean; isCheapest: boolean };
export type StationSortMode = "distance" | "price";

type HighlightStation = {
  station_id?: string;
  station_name?: string;
  brand?: string;
  price?: number | null;
  currency?: string | null;
  distance?: number | null;
  is_open?: boolean;
  street?: string;
  house_number?: string;
  postcode?: string | number;
  place?: string;
  latitude?: number | null;
  longitude?: number | null;
  price_age_hours?: number | null;
  price_stale?: boolean | null;
  fuel_type?: string | null;
  requested_fuel?: string | null;
  fallback_used?: boolean;
  provider?: string | null;
  fuel_prices?: Record<string, number | null>;
  fuel_fallbacks?: Record<string, boolean>;
};

export type NavigationProvider = "auto" | "apple" | "google" | "waze";
export type CardDisplayMode = "compact" | "detailed" | "custom";
export type CustomLayout = "list" | "highlights_list" | "configured_list";
export type CardSortMode = StationSortMode;
export type CardDensity = "compact" | "normal";
export type CardConfig = {
  type?: string;
  entity?: string;
  navigation?: boolean;
  navigation_provider?: NavigationProvider;
  show_brand_logos?: boolean;
  logo_path?: string;
  display_mode?: CardDisplayMode;
  custom_layout?: CustomLayout;
  sort_mode?: CardSortMode;
  sort_fuel?: string;
  visible_station_count?: number;
  title?: string;
  show_title?: boolean;
  show_station_count?: boolean;
  show_radius?: boolean;
  show_fuel_type?: boolean;
  show_last_updated?: boolean;
  show_provider?: boolean;
  show_fetch_mode?: boolean;
  show_diagnostics?: boolean;
  show_refresh?: boolean;
  show_name?: boolean;
  name_mode?: "full" | "short";
  show_address?: boolean;
  show_status?: boolean;
  show_distance?: boolean;
  show_prices?: boolean;
  show_fuel_labels?: boolean;
  show_provider_row?: boolean;
  show_badges?: boolean;
  density?: CardDensity;
  show_dividers?: boolean;
};

const DEFAULT_CARD_CONFIG: CardConfig = {
  navigation: true,
  navigation_provider: "auto",
  show_brand_logos: true,
  logo_path: "/mobile_fuel_stations/logos/",
  display_mode: "detailed",
  custom_layout: "list",
  visible_station_count: 0,
  show_title: true,
  show_station_count: true,
  show_radius: true,
  show_fuel_type: true,
  show_last_updated: true,
  show_provider: true,
  show_fetch_mode: true,
  show_diagnostics: true,
  show_refresh: true,
  show_name: true,
  name_mode: "full",
  show_address: true,
  show_status: true,
  show_distance: true,
  show_prices: true,
  show_fuel_labels: true,
  show_provider_row: true,
  show_badges: true,
  density: "normal",
  show_dividers: true,
};

function normalizeCardConfig(config: Partial<CardConfig> = {}): CardConfig {
  const merged: CardConfig = {
    ...DEFAULT_CARD_CONFIG,
    ...config,
    type: config.type ?? "custom:mobile-fuel-stations-card",
    navigation: config.navigation !== false,
    navigation_provider: config.navigation_provider ?? "auto",
    show_brand_logos: config.show_brand_logos !== false,
    logo_path: config.logo_path ?? DEFAULT_LOGO_PATH,
    display_mode: config.display_mode ?? "detailed",
    custom_layout: config.custom_layout ?? "list",
    density: config.density ?? "normal",
    name_mode: config.name_mode ?? "full",
  };
  const count = Number(config.visible_station_count);
  merged.visible_station_count = Number.isInteger(count) && count > 0 ? count : 0;
  // A card must retain at least one identifying field even if a hand-written
  // configuration disables all optional station text fields.
  if (merged.show_name === false && merged.show_address === false) merged.show_name = true;
  return merged;
}

const unavailable = new Set(["unknown", "unavailable"]);
export const DEFAULT_LOGO_PATH = "/mobile_fuel_stations/logos/";

const BUNDLED_LOGO_FILES: Record<string, string> = {
  aral: "aral.png", jet: "jet.png", omv: "omv.png", orlen: "orlen.png", shell: "shell.png", total: "total.png",
  access: "access.png", "agip-eni": "agip-eni.png", allguth: "allguth.png", "avia-xpress": "avia-xpress.png", avia: "avia.png",
  baywa: "baywa.png", "bell-oil": "bell-oil.png", bft: "bft.png", calpam: "calpam.png", "citi-oil-sb-tankstelle": "citi-oil-sb-tankstelle.png",
  classic: "classic.png", "e-center": "e-center.png", ed: "ed.png", edeka: "edeka.png", elan: "elan.png", esso: "esso.png",
  feneberg: "feneberg.png", "flaeming-tank": "flaeming-tank.png", globus: "globus.png", greenline: "greenline.png", gruene: "gruene.png",
  gulf: "gulf.png", hem: "hem.png", hessol: "hessol.png", hornbach: "hornbach.png", hoyer: "hoyer.png", joiss: "joiss.png",
  "kk-klaas-kock": "kk-klaas-kock.png", minera: "minera.png", mol: "mol.png", "mr-wash-autoservice-ag": "mr-wash-autoservice-ag.png",
  mtb: "mtb.png", "mundorf-tank": "mundorf-tank.png", nordoel: "nordoel.png", oil: "oil.png", oktan: "oktan.png", pin: "pin.png",
  q1: "q1.png", raiffeisen: "raiffeisen.png", ran: "ran.png", "roth-energie": "roth-energie.png", sb: "sb.png",
  "schillhorn-tankstelle": "schillhorn-tankstelle.png", schindele: "schindele.png", score: "score.png", spreves: "spreves.png",
  sprint: "sprint.png", star: "star.png", "supermarkt-tankstelle": "supermarkt-tankstelle.png", team: "team.png", tinq: "tinq.png",
  trigema: "trigema.png", "v-markt": "v-markt.png", westfalen: "westfalen.png",
};

const BUNDLED_LOGO_KEYS = new Set(Object.keys(BUNDLED_LOGO_FILES));

const BRAND_ALIASES: Record<string, string> = {
  aral: "aral",
  shell: "shell",
  esso: "esso",
  jet: "jet",
  "j e t": "jet",
  total: "total",
  "total energies": "total",
  totalenergies: "total",
  hem: "hem",
  avia: "avia",
  "avia express": "avia-xpress",
  "avia xpress": "avia-xpress",
  orlen: "orlen",
  "orlen express": "orlen",
  omv: "omv",
  q1: "q1",
  "q 1": "q1",
  raiffeisen: "raiffeisen",
  oil: "oil",
  "oil tankstelle": "oil",
  star: "star",
  bft: "bft",
  westfalen: "westfalen",
  sprint: "sprint",
  hoyer: "hoyer",
  classic: "classic",
  team: "team",
  ed: "ed",
  "freie tankstelle": "freie-tankstelle",
  baywa: "baywa",
  globus: "globus",
  access: "access",
  allguth: "allguth",
  "bell oil": "bell-oil",
  calpam: "calpam",
  "citi oil sb tankstelle": "citi-oil-sb-tankstelle",
  "e center": "e-center",
  elan: "elan",
  feneberg: "feneberg",
  "flaeming tank": "flaeming-tank",
  "flaming tank": "flaeming-tank",
  greenline: "greenline",
  gruene: "gruene",
  grune: "gruene",
  hessol: "hessol",
  hornbach: "hornbach",
  "jantzon tankstelle": "aral",
  joiss: "joiss",
  "k k klaas and kock": "kk-klaas-kock",
  "k k klaas kock": "kk-klaas-kock",
  "kk klaas kock": "kk-klaas-kock",
  "minera automatenstation": "minera",
  minera: "minera",
  "mr wash autoservice ag": "mr-wash-autoservice-ag",
  mtb: "mtb",
  "mundorf tank": "mundorf-tank",
  nordoel: "nordoel",
  oktan: "oktan",
  pin: "pin",
  ran: "ran",
  "roth energie": "roth-energie",
  sb: "sb",
  schillhorn: "schillhorn-tankstelle",
  "schillhorn tankstelle": "schillhorn-tankstelle",
  schindele: "schindele",
  score: "score",
  spreves: "spreves",
  "supermarkt tankstelle": "supermarkt-tankstelle",
  trigema: "trigema",
  "v markt": "v-markt",
  svg: "svg",
  kaufland: "kaufland",
  edeka: "edeka",
  eni: "agip-eni",
  agip: "agip-eni",
  "agip eni": "agip-eni",
  "eni agip eni": "agip-eni",
  bp: "bp",
  mol: "mol",
  "circle k": "circle-k",
  q8: "q8",
  tamoil: "tamoil",
  avanti: "avanti",
  turmol: "turmol",
  socar: "socar",
  ina: "ina",
  petrol: "petrol",
  rompetrol: "rompetrol",
  lukoil: "lukoil",
  "nis petrol": "nis-petrol",
  gazprom: "gazprom",
  okko: "okko",
  wog: "wog",
  gulf: "gulf",
  tinq: "tinq",
};

function normalizeBrand(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("en-US")
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function resolveBrandLogoKey(brand: unknown, stationName?: unknown): string | null {
  const normalizedBrand = typeof brand === "string" ? normalizeBrand(brand) : "";
  const direct = normalizedBrand ? BRAND_ALIASES[normalizedBrand] : undefined;
  if (direct) return direct;
  const candidates = [normalizedBrand, typeof stationName === "string" ? normalizeBrand(stationName) : ""];
  for (const candidate of candidates) {
    if (!candidate) continue;
    const candidateWords = new Set(candidate.split(" "));
    for (const [alias, key] of Object.entries(BRAND_ALIASES)) {
      const ambiguousShortAliases = new Set(["ed", "sb", "oil", "pin", "q1", "svg"]);
      if (BUNDLED_LOGO_KEYS.has(key) && (alias.includes(" ") || !ambiguousShortAliases.has(alias)) && alias.split(" ").every((word) => candidateWords.has(word))) return key;
    }
  }
  return null;
}

export function normalizeLogoPath(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const path = value.trim();
  if (!path || !path.startsWith("/") || path.includes("\\") || path.includes("..") || path.includes("%")) return null;
  if (/[\u0000-\u001f\u007f?#]/.test(path) || /^(?:[a-z][a-z0-9+.-]*:)?\/\//i.test(path)) return null;
  if (!/^\/(?:local|hacsfiles|mobile_fuel_stations)(?:\/[A-Za-z0-9._~!$&'()*+,;=:@%-]+)+\/?$/.test(path)) return null;
  return `${path.replace(/\/+$/, "")}/`;
}

export function buildBrandLogoUrl(brand: unknown, logoPath: unknown = DEFAULT_LOGO_PATH, stationName?: unknown): string | null {
  const key = resolveBrandLogoKey(brand, stationName);
  const base = normalizeLogoPath(logoPath);
  if (!key || !base) return null;
  if (base === DEFAULT_LOGO_PATH && !BUNDLED_LOGO_KEYS.has(key)) return null;
  const filename = BUNDLED_LOGO_FILES[key] ?? `${key}.svg`;
  return `${base}${filename}`;
}

export function formatPrice(value: unknown, locale = "de-DE", currency = "EUR"): string | null {
  if (value === null || value === undefined || value === "") return null;
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(number)) return null;
  const unit = currency.toUpperCase() === "EUR" ? "€/l" : `${currency.toUpperCase()}/l`;
  return `${new Intl.NumberFormat(locale, { minimumFractionDigits: 3, maximumFractionDigits: 3 }).format(number)} ${unit}`;
}

export function formatDistance(value: unknown, locale = "de-DE"): string | null {
  if (value === null || value === undefined || value === "") return null;
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(number)) return null;
  return `${new Intl.NumberFormat(locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(number)} km`;
}

export function fuelLabel(value: unknown): string | null {
  const labels: Record<string, string> = {
    diesel: "Diesel",
    e5: "E5",
    e10: "E10",
    lpg: "LPG / Autogas",
    hvo100: "HVO100",
  };
  return typeof value === "string" ? labels[value.toLowerCase()] ?? value : null;
}

function normalizeText(value: string): string {
  return value.toLocaleLowerCase().replace(/[\p{P}\p{S}]+/gu, " ").replace(/\s+/g, " ").trim();
}

export function shouldShowBrand(name: unknown, brand: unknown): boolean {
  if (typeof name !== "string" || typeof brand !== "string") return false;
  const normalizedName = normalizeText(name);
  const normalizedBrand = normalizeText(brand);
  if (!normalizedBrand || !normalizedName) return false;
  const nameWords = new Set(normalizedName.split(" "));
  return !normalizedBrand.split(" ").every((word) => nameWords.has(word));
}

export function validCoordinate(value: unknown, minimum: number, maximum: number): number | null {
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) && number >= minimum && number <= maximum ? number : null;
}

export function detectNavigationProvider(provider: NavigationProvider = "auto", userAgent = globalThis.navigator?.userAgent ?? "", maxTouchPoints = globalThis.navigator?.maxTouchPoints ?? 0): Exclude<NavigationProvider, "auto"> {
  if (provider === "apple" || provider === "google" || provider === "waze") return provider;
  const isIOS = /iPhone|iPad|iPod/i.test(userAgent) || (/Macintosh/i.test(userAgent) && /Mac OS X/i.test(userAgent) && maxTouchPoints > 1);
  return isIOS ? "apple" : "google";
}

export function buildNavigationUrl(latitude: unknown, longitude: unknown, provider: NavigationProvider = "auto", label?: string, userAgent?: string): string | null {
  const lat = validCoordinate(latitude, -90, 90);
  const lon = validCoordinate(longitude, -180, 180);
  if (lat === null || lon === null) return null;
  const resolvedProvider = detectNavigationProvider(provider, userAgent);
  if (resolvedProvider === "apple") {
    return `https://maps.apple.com/directions?destination=${encodeURIComponent(`${lat},${lon}`)}&mode=driving`;
  }
  if (resolvedProvider === "waze") {
    return `https://www.waze.com/ul?ll=${encodeURIComponent(`${lat},${lon}`)}&navigate=yes`;
  }
  return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(`${lat},${lon}`)}&travelmode=driving&dir_action=navigate`;
}

export function discoverStationEntities(overviewId: string, overview: HassState, hass: Hass): string[] {
  const configured = overview.attributes.station_entities;
  if (Array.isArray(configured)) {
    return configured.filter((id): id is string => typeof id === "string" && isUsableStation(hass.states[id]));
  }

  // v0.1 fallback: only inspect the same overview prefix and existing states.
  const prefix = overviewId.match(/^(sensor\..+)_nearby_stations$/)?.[1];
  if (!prefix) return [];
  const rawCount = Number(overview.attributes.station_count);
  const count = Number.isInteger(rawCount) && rawCount > 0 ? Math.min(rawCount, 10) : 10;
  return Array.from({ length: count }, (_, index) => `${prefix}_station_${index + 1}`)
    .filter((id) => isUsableStation(hass.states[id]));
}

function isUsableStation(state: HassState | undefined): boolean {
  return Boolean(state && !unavailable.has(state.state));
}

const MOBILE_FUEL_STATIONS_ENTITY_PREFIX = "sensor.mobile_fuel_stations_";

export function isOverviewEntity(entityId: string, state: HassState | undefined): boolean {
  if (!entityId.startsWith("sensor.") || !state) return false;
  if (Array.isArray(state.attributes.station_entities)) return true;
  const mobileFuelMarkers = ["location_entity", "radius", "fuel_type", "station_count"]
    .filter((key) => state.attributes[key] !== undefined).length;
  if (entityId.endsWith("_nearby_stations") && mobileFuelMarkers >= 2) return true;

  // HA omits extra attributes while an entity is unavailable.  The stable
  // integration-owned entity-id prefix is the remaining client-side marker;
  // it keeps unavailable/unknown entries selectable without treating foreign
  // sensors with a similar suffix as Mobile Fuel Stations entities.
  return entityId.startsWith(MOBILE_FUEL_STATIONS_ENTITY_PREFIX)
    && entityId.endsWith("_nearby_stations");
}

export function findOverviewEntity(hass: Hass | undefined, entities: string[] = [], entitiesFallback: string[] = []): string | undefined {
  const suggested = [...new Set([...entities, ...entitiesFallback])]
    .filter((entityId) => isOverviewEntity(entityId, hass?.states[entityId]))
    .sort();
  if (suggested.length) return suggested[0];
  return Object.keys(hass?.states ?? {})
    .filter((entityId) => isOverviewEntity(entityId, hass?.states[entityId]))
    .sort()[0];
}

function text(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function finiteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? number : null;
}

function finitePositiveNumber(value: unknown): number | null {
  const number = finiteNumber(value);
  return number !== null && number > 0 ? number : null;
}

function stableCompare(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

function stationIdentity(row: StationRow): string {
  return text(row.state.attributes.station_id) ?? row.id;
}

function stationDistance(row: StationRow): number | null {
  const distance = finiteNumber(row.state.attributes.distance);
  return distance !== null && distance >= 0 ? distance : null;
}

function stationPrice(row: StationRow, fuel: string): number | null {
  const attributes = row.state.attributes;
  if (attributes.price_stale === true || !fuel) return null;
  const prices = attributes.fuel_prices;
  if (prices && typeof prices === "object") {
    return finitePositiveNumber((prices as Record<string, unknown>)[fuel]);
  }
  const stationFuel = text(attributes.requested_fuel) ?? text(attributes.fuel_type);
  return stationFuel?.toLowerCase() === fuel.toLowerCase()
    ? finitePositiveNumber(row.state.state)
    : null;
}

export function prioritizeStations(
  stations: StationRow[],
  sortMode: StationSortMode = "distance",
  sortFuelType = "diesel",
): StationPriority[] {
  const unique = new Map<string, StationRow>();
  for (const row of stations) {
    const identity = stationIdentity(row);
    if (!unique.has(identity)) unique.set(identity, row);
  }
  const rows = [...unique.values()];
  const nearest = rows
    .filter((row) => stationDistance(row) !== null)
    .sort((left, right) => (stationDistance(left)! - stationDistance(right)!) || stableCompare(stationIdentity(left), stationIdentity(right)))[0];
  const cheapest = rows
    .filter((row) => stationPrice(row, sortFuelType) !== null)
    .sort((left, right) => (
      stationPrice(left, sortFuelType)! - stationPrice(right, sortFuelType)!
      || (stationDistance(left) ?? Number.POSITIVE_INFINITY) - (stationDistance(right) ?? Number.POSITIVE_INFINITY)
      || stableCompare(stationIdentity(left), stationIdentity(right))
    ))[0];
  const ordered = rows
    .filter((row) => row !== nearest && row !== cheapest)
    .sort((left, right) => {
      const leftDistance = stationDistance(left) ?? Number.POSITIVE_INFINITY;
      const rightDistance = stationDistance(right) ?? Number.POSITIVE_INFINITY;
      if (sortMode === "price") {
        const leftPrice = stationPrice(left, sortFuelType) ?? Number.POSITIVE_INFINITY;
        const rightPrice = stationPrice(right, sortFuelType) ?? Number.POSITIVE_INFINITY;
        return leftPrice - rightPrice || leftDistance - rightDistance || stableCompare(stationIdentity(left), stationIdentity(right));
      }
      return leftDistance - rightDistance || stableCompare(stationIdentity(left), stationIdentity(right));
    });
  const prioritized = [nearest, cheapest, ...ordered].filter((row, index, all): row is StationRow => Boolean(row) && all.indexOf(row) === index);
  return prioritized.map((row) => ({
    ...row,
    isNearest: row === nearest,
    isCheapest: row === cheapest,
  }));
}

export class MobileFuelStationsCard extends LitElement {
  static styles = css`
    :host { display: block; container-type: inline-size; }
    ha-card { padding: 16px; color: var(--primary-text-color); background: var(--card-background-color); border-radius: var(--ha-card-border-radius, 12px); }
    .header { display: block; margin-bottom: 12px; }
    h2 { margin: 0; font-size: 1.1rem; }
    .summary, .secondary { color: var(--secondary-text-color); font-size: .9rem; }
    .summary { display: block; margin-top: 4px; }
    .stations { display: grid; gap: 4px; }
    .station { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto auto; gap: 8px; align-items: center; border-top: 1px solid var(--divider-color); padding: 8px 0; cursor: pointer; min-width: 0; }
    .station:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .icon { color: var(--primary-color); font-size: 1.5rem; }
    .brand-logo { width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; }
    .brand-logo img { display: block; width: 100%; height: 100%; object-fit: contain; }
    .name, .address { overflow-wrap: break-word; word-break: normal; hyphens: auto; min-width: 0; }
    .name { font-weight: 500; }
    .address { color: var(--secondary-text-color); font-size: .85rem; }
    .price { font-size: 1.05rem; font-weight: 700; text-align: right; white-space: nowrap; }
    .prices { min-width: 0; text-align: right; }
    .fuel-price { display: flex; justify-content: flex-end; gap: 6px; flex-wrap: wrap; font-size: .9rem; }
    .fuel-price strong { white-space: nowrap; }
    .meta { color: var(--secondary-text-color); font-size: .82rem; text-align: right; white-space: nowrap; }
    .navigate { color: var(--primary-color); display: inline-flex; align-items: center; justify-content: center; padding: 8px; min-width: 44px; min-height: 44px; box-sizing: border-box; border-radius: 50%; }
    .navigate:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .open { color: var(--success-color, var(--primary-color)); }
    .closed { color: var(--secondary-text-color); }
    .message { color: var(--secondary-text-color); }
    .stale-warning { color: var(--warning-color, var(--primary-color)); margin: 0 0 10px; font-size: .9rem; }
    .control-error { color: var(--error-color, var(--warning-color, var(--primary-color))); margin: 0 0 10px; font-size: .9rem; }
    .controls { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 0 0 12px; padding: 8px 0; border-top: 1px solid var(--divider-color); border-bottom: 1px solid var(--divider-color); }
    .control-label { color: var(--secondary-text-color); font-size: .85rem; }
    .mode-switch { display: inline-flex; border: 1px solid var(--divider-color); border-radius: 999px; overflow: hidden; }
    .controls button { color: var(--primary-text-color); background: var(--card-background-color); border: 0; padding: 6px 10px; cursor: pointer; font: inherit; }
    .controls button.selected { color: var(--text-primary-color, var(--primary-text-color)); background: var(--primary-color); }
    .controls button:disabled { cursor: default; opacity: .65; }
    .controls .refresh { margin-left: auto; border: 1px solid var(--primary-color); border-radius: 999px; }
    .highlights { display: grid; gap: 6px; margin-bottom: 10px; }
    .highlight { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto auto; gap: 8px; align-items: center; border: 1px solid var(--divider-color); border-radius: var(--ha-card-border-radius, 12px); padding: 8px 10px; min-width: 0; }
    .highlight.is-link { cursor: pointer; }
    .highlight.is-link:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .highlight-label { color: var(--secondary-text-color); font-size: .82rem; font-weight: 600; text-transform: uppercase; }
    .highlight-name { font-weight: 600; margin-top: 3px; overflow-wrap: break-word; word-break: normal; hyphens: auto; min-width: 0; }
    .highlight-meta { color: var(--secondary-text-color); font-size: .9rem; margin-top: 3px; }
    .provider { color: var(--secondary-text-color); font-size: .8rem; margin-top: 3px; }
    .station-badges { display: inline-flex; gap: 4px; flex-wrap: wrap; margin-left: 4px; vertical-align: middle; }
    .station-badge { display: inline-flex; align-items: center; gap: 2px; color: var(--secondary-text-color); font-size: .72rem; white-space: nowrap; }
    .station-badge ha-icon { --mdc-icon-size: 14px; }
    .station-badge.cheapest { color: var(--primary-color); }
    .detailed-mode .station-badge { border: 1px solid currentColor; border-radius: 999px; padding: 1px 5px; font-size: .72rem; font-weight: 600; }
    .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
    .diagnostics { margin: 0 0 10px; border-top: 1px solid var(--divider-color); border-bottom: 1px solid var(--divider-color); }
    .diagnostics summary { cursor: pointer; padding: 7px 0; color: var(--secondary-text-color); font-size: .85rem; }
    .diagnostics .provider-status-list { padding: 0 0 7px; }
    .custom-mode .header { margin-bottom: 8px; }
    .no-dividers .station { border-top: 0; }
    .custom-mode .stations { gap: 4px; }
    .custom-mode.dense .stations { gap: 0; }
    .custom-mode.dense .stations .station { padding-top: 3px; padding-bottom: 3px; }
    .custom-mode .featured-stations { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-bottom: 8px; }
    .custom-mode .featured-station { display: flex; flex-direction: column; min-width: 0; height: 100%; box-sizing: border-box; border: 1px solid var(--divider-color); border-radius: var(--ha-card-border-radius, 12px); padding: 8px; cursor: pointer; }
    .custom-mode .featured-station:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .featured-top { display: grid; grid-template-columns: 32px minmax(0, 1fr) 40px; gap: 6px; align-items: center; min-width: 0; }
    .featured-main { min-width: 0; }
    .featured-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
    .featured-values { display: flex; align-items: baseline; justify-content: space-between; gap: 6px; margin-top: auto; padding-top: 6px; min-width: 0; }
    .featured-values .price { font-size: 1rem; }
    .featured-values .meta { overflow: hidden; text-overflow: ellipsis; }
    .featured-station .navigate { min-width: 40px; min-height: 40px; padding: 6px; }
    .featured-station.no-logo .featured-top { grid-template-columns: minmax(0, 1fr) 40px; }
    .featured-station.no-logo.no-navigation .featured-top { grid-template-columns: minmax(0, 1fr); }
    .custom-mode .detail-meta { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 6px; color: var(--secondary-text-color); font-size: .8rem; line-height: 1.2; }
    .custom-mode .custom-station { grid-template-columns: 32px minmax(0, 1fr) auto; }
    .custom-mode .custom-station.no-logo { grid-template-columns: minmax(0, 1fr) auto; }
    .custom-mode .custom-station.no-navigation { grid-template-columns: 32px minmax(0, 1fr); }
    .custom-mode .custom-station.no-logo.no-navigation { grid-template-columns: minmax(0, 1fr); }
    .custom-mode .custom-primary { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px; align-items: start; min-width: 0; }
    .custom-mode .custom-prices { min-width: 0; text-align: right; }
    .custom-mode .custom-prices .fuel-price { justify-content: flex-end; }
    .custom-mode.dense .custom-station { padding-top: 2px; padding-bottom: 2px; gap: 4px; }
    .custom-mode.dense .custom-primary { gap: 4px; }
    .custom-mode.dense .custom-prices { font-size: .82rem; line-height: 1.05; }
    .custom-mode.dense .custom-prices .fuel-price { gap: 3px; }
    .custom-mode.dense .custom-station .address { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .custom-mode.dense .station { gap: 6px; }
    .custom-mode.dense .address { font-size: .78rem; line-height: 1.15; }
    .custom-mode.dense .detail-meta { gap: 1px 4px; font-size: .74rem; line-height: 1.1; }
    .custom-mode .name.short { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .custom-mode .station-field-hidden { display: none; }
    .custom-mode .station.no-address .station-main { min-height: 2.2em; }
    .station.no-logo { grid-template-columns: minmax(0, 1fr) auto auto; }
    .station.no-navigation { grid-template-columns: 32px minmax(0, 1fr) auto; }
    .station.no-logo.no-navigation { grid-template-columns: minmax(0, 1fr) auto; }
    .station.no-prices { grid-template-columns: 32px minmax(0, 1fr) auto; }
    .station.no-logo.no-prices { grid-template-columns: minmax(0, 1fr) auto; }
    .station.no-navigation.no-prices { grid-template-columns: 32px minmax(0, 1fr); }
    .station.no-logo.no-navigation.no-prices { grid-template-columns: minmax(0, 1fr); }
    .compact-mode ha-card { padding: 10px 12px; }
    .compact-mode .header { margin-bottom: 6px; }
    .compact-mode .controls { margin-bottom: 6px; padding: 5px 0; }
    .compact-mode .station { padding: 4px 0; gap: 6px; }
    .compact-station { grid-template-columns: 36px minmax(0, 1fr) auto auto; min-height: 56px; }
    .compact-station .station-main { min-width: 0; }
    .compact-station .station-meta { display: flex; align-items: center; gap: 8px; min-width: 0; color: var(--secondary-text-color); font-size: .75rem; line-height: 1.15; white-space: nowrap; }
    .compact-station .station-meta > * { overflow: hidden; text-overflow: ellipsis; }
    .compact-mode .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .compact-mode .address { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .compact-mode .provider { display: none; }
    .compact-mode .prices { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }
    .compact-mode .fuel-price { display: grid; justify-items: end; gap: 0; line-height: 1.1; }
    .compact-mode .fuel-price strong { font-size: .95rem; }
    .compact-mode .fuel-price > span { color: var(--secondary-text-color); font-size: .72rem; }
    .compact-mode .meta { margin-left: 0; }
    .compact-mode .navigate { min-width: 36px; min-height: 36px; padding: 5px; }
    .compact-mode .brand-logo, .compact-mode .icon { width: 36px; height: 36px; }
    .stations { grid-template-columns: minmax(0, 1fr); }
    @container (min-width: 600px) {
      .highlights { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .header { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
      .summary { margin-top: 0; }
      .station { grid-template-columns: 32px minmax(12rem, 1fr) minmax(8rem, auto) auto; }
      .station.no-logo { grid-template-columns: minmax(12rem, 1fr) minmax(8rem, auto) auto; }
      .station.no-navigation { grid-template-columns: 32px minmax(12rem, 1fr) minmax(8rem, auto); }
      .station.no-logo.no-navigation { grid-template-columns: minmax(12rem, 1fr) minmax(8rem, auto); }
      .station.no-prices { grid-template-columns: 32px minmax(12rem, 1fr) auto; }
      .station.no-logo.no-prices { grid-template-columns: minmax(12rem, 1fr) auto; }
      .station.no-navigation.no-prices { grid-template-columns: 32px minmax(12rem, 1fr); }
      .station.no-logo.no-navigation.no-prices { grid-template-columns: minmax(12rem, 1fr); }
      .compact-mode .station { grid-template-columns: 36px minmax(12rem, 1fr) auto auto; }
      .compact-mode .station.no-logo { grid-template-columns: minmax(12rem, 1fr) auto auto; }
      .compact-mode .station.no-navigation { grid-template-columns: 36px minmax(12rem, 1fr) auto; }
      .compact-mode .station.no-logo.no-navigation { grid-template-columns: minmax(12rem, 1fr) auto; }
    }
    @container (max-width: 599px) {
      ha-card { padding: 12px; }
      .station { grid-template-columns: 26px minmax(0, 1fr) auto; gap: 6px; }
      .station .prices { grid-column: 2; grid-row: 2; text-align: left; }
      .fuel-price { justify-content: flex-start; gap: 4px; }
      .station .navigate { grid-column: 3; grid-row: 1 / span 2; align-self: center; }
      .station.no-logo { grid-template-columns: minmax(0, 1fr) auto; }
      .station.no-navigation { grid-template-columns: 26px minmax(0, 1fr); }
      .station.no-logo.no-navigation { grid-template-columns: minmax(0, 1fr); }
      .station.no-prices { grid-template-columns: 26px minmax(0, 1fr); }
      .station.no-logo.no-prices { grid-template-columns: minmax(0, 1fr); }
      .station.no-navigation.no-prices { grid-template-columns: 26px minmax(0, 1fr); }
      .station.no-logo.no-navigation.no-prices { grid-template-columns: minmax(0, 1fr); }
      .station.no-navigation .prices { grid-column: 2; }
      .compact-mode .station { grid-template-columns: 36px minmax(0, 1fr) minmax(92px, auto) 36px; gap: 5px; }
      .compact-mode .station .prices { grid-column: 3; grid-row: 1; justify-content: flex-end; flex-wrap: nowrap; text-align: right; }
      .compact-mode .station .navigate { grid-column: 4; grid-row: 1; align-self: center; }
      .compact-mode .station.no-logo { grid-template-columns: minmax(0, 1fr) minmax(92px, auto) 36px; }
      .compact-mode .station.no-navigation { grid-template-columns: 36px minmax(0, 1fr) minmax(92px, auto); }
      .compact-mode .station.no-logo.no-navigation { grid-template-columns: minmax(0, 1fr) minmax(92px, auto); }
      .compact-mode .station.no-prices { grid-template-columns: 36px minmax(0, 1fr) 36px; }
      .compact-mode .station.no-logo.no-prices { grid-template-columns: minmax(0, 1fr) 36px; }
      .compact-mode .station.no-navigation.no-prices { grid-template-columns: 36px minmax(0, 1fr); }
      .compact-mode .station.no-logo.no-navigation.no-prices { grid-template-columns: minmax(0, 1fr); }
      .compact-mode .fuel-price { min-width: 42px; }
      .highlight { grid-template-columns: 26px minmax(0, 1fr) auto auto; gap: 6px; }
      .highlight .navigate { grid-column: auto; }
    }
    @container (max-width: 359px) {
      .custom-mode .featured-stations { grid-template-columns: 1fr; }
      .compact-mode .station { grid-template-columns: 32px minmax(0, 1fr) 36px; }
      .compact-mode .brand-logo, .compact-mode .icon { width: 32px; height: 32px; }
      .compact-mode .station .prices { grid-column: 2; grid-row: 2; justify-content: flex-start; flex-wrap: wrap; text-align: left; }
      .compact-mode .station .navigate { grid-column: 3; grid-row: 1 / span 2; }
      .compact-mode .station.no-logo { grid-template-columns: minmax(0, 1fr) 36px; }
      .compact-mode .station.no-navigation { grid-template-columns: 32px minmax(0, 1fr); }
      .compact-mode .station.no-logo.no-navigation { grid-template-columns: minmax(0, 1fr); }
      .compact-mode .station.no-prices { grid-template-columns: 32px minmax(0, 1fr) 36px; }
      .compact-mode .station.no-logo.no-prices { grid-template-columns: minmax(0, 1fr) 36px; }
      .compact-mode .station.no-navigation.no-prices { grid-template-columns: 32px minmax(0, 1fr); }
      .compact-mode .station.no-logo.no-navigation.no-prices { grid-template-columns: minmax(0, 1fr); }
    }
  `;

  private _config?: CardConfig;
  private _hass?: Hass;
  private _configError?: string;
  private _controlError?: string;
  private _failedBrandLogos = new Set<string>();
  private _manualRefreshInFlight = false;
  private _modeChangeInFlight = false;
  private _cooldownTimer?: number;
  private _cooldownObservedAt = 0;
  private _cooldownObservedSeconds = 0;

  setConfig(config: Partial<CardConfig>): void {
    if (!config || typeof config.entity !== "string" || !config.entity.trim()) {
      this._config = normalizeCardConfig(config);
      this._configError = this._text("selectEntity");
      this.requestUpdate();
      return;
    }
    this._config = normalizeCardConfig(config);
    this._configError = undefined;
    this.requestUpdate();
  }

  set hass(value: Hass) { this._hass = value; this.requestUpdate(); }
  get hass(): Hass | undefined { return this._hass; }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this._cooldownTimer !== undefined) window.clearInterval(this._cooldownTimer);
    this._cooldownTimer = undefined;
  }

  static getConfigElement(): HTMLElement { return document.createElement("mobile-fuel-stations-card-editor"); }
  static getStubConfig(hass?: Hass, entities: string[] = [], entitiesFallback: string[] = []): CardConfig {
    const entity = findOverviewEntity(hass, entities, entitiesFallback);
    return normalizeCardConfig(entity ? { entity, navigation: true, display_mode: "compact" } : { navigation: true, display_mode: "compact" });
  }

  protected render() {
    if (this._configError) return this._message(this._configError);
    if (!this._config || !this._hass) return this._message(this._text("unavailable"));
    const entity = this._config.entity;
    if (!entity) return this._message(this._text("notFound"));
    const overview = this._hass.states[entity];
    if (!overview) return this._message(this._text("notFound"));
    const ids = discoverStationEntities(entity, overview, this._hass);
    const discoveredStations = ids.map((id) => ({ id, state: this._hass!.states[id]! })).filter(({ state }) => isUsableStation(state));
    const isUnavailable = unavailable.has(overview.state);
    const cooldown = this._cooldownState(overview);
    const compact = this._config.display_mode === "compact";
    const custom = this._config.display_mode === "custom";
    const sortMode = this._config.sort_mode ?? (overview.attributes.sort_mode === "price" ? "price" : "distance");
    const sortFuel = this._config.sort_fuel ?? text(overview.attributes.sort_fuel) ?? text(overview.attributes.fuel_type) ?? "diesel";
    const prioritized = prioritizeStations(discoveredStations, sortMode, sortFuel);
    const count = this._config.visible_station_count ?? 0;
    const stations = count > 0 ? prioritized.slice(0, count) : prioritized;
    const classes = [custom ? "custom-mode" : compact ? "compact-mode" : "detailed-mode", this._config.density === "compact" ? "dense" : "", this._config.show_dividers === false ? "no-dividers" : ""].filter(Boolean).join(" ");
    const featured = custom && this._config.custom_layout === "highlights_list" ? stations.slice(0, Math.min(2, stations.length)) : [];
    const list = featured.length ? stations.slice(featured.length) : stations;
    return html`
      <div class=${classes}>
      <ha-card>
        ${this._header(overview, stations)}
        ${this._controls(overview, cooldown, !custom || this._config.show_fetch_mode !== false, !custom || this._config.show_refresh !== false)}
        ${this._providerStatus(overview, compact, !custom || this._config.show_diagnostics !== false)}
        ${this._controlError ? html`<div class="control-error" role="alert">${this._controlError}</div>` : nothing}
        ${isUnavailable ? html`<div class="message" role="status">${this._text("unavailable")}</div>` : nothing}
        ${!isUnavailable && this._hasRefreshError(overview) ? html`<div class="stale-warning" role="alert">${this._refreshError(overview, cooldown.display)}</div>` : nothing}
        ${!isUnavailable && this._fallbackMessage(overview) ? html`<div class="secondary" role="status">${this._fallbackMessage(overview)}</div>` : nothing}
        ${!isUnavailable && overview.attributes.data_stale === true ? html`<div class="stale-warning" role="status">${this._staleMessage(overview)}</div>` : nothing}
        ${!isUnavailable && overview.attributes.data_stale !== true && stations.some(({ state }) => state.attributes.price_stale === true) ? html`<div class="stale-warning" role="status">${this._text("providerPricesStale")}</div>` : nothing}
        ${this._hasNakordoni(overview, discoveredStations) ? html`<div class="secondary"><a href="https://nakordoni.eu" target="_blank" rel="noopener">Data by nakordoni.eu</a></div>` : nothing}
        ${!isUnavailable ? (stations.length ? html`${featured.length ? html`<div class="featured-stations">${featured.map((station) => this._featuredStation(station))}</div>` : nothing}<div class="stations">${list.map((station) => this._station(station, compact))}</div>` : html`<div class="message">${this._text("none")}</div>`) : nothing}
      </ha-card>
      </div>
    `;
  }

  private _header(overview: HassState, stations: Array<{ id: string; state: HassState }>) {
    const custom = this._config?.display_mode === "custom";
    const showTitle = !custom || this._config?.show_title !== false;
    const summary = this._summary(overview, stations, custom ? this._config : undefined);
    if (!showTitle && !summary) return nothing;
    return html`<div class="header">${showTitle ? html`<h2>${custom && this._config?.title ? this._config.title : this._text("title")}</h2>` : nothing}${summary ? html`<span class="summary">${summary}</span>` : nothing}</div>`;
  }

  private _controls(overview: HassState, cooldown: { backend: number; display: number }, showMode = true, showRefresh = true) {
    const entryId = text(overview.attributes.config_entry_id);
    if (!entryId || !this._hass?.callService || this._hass.user?.is_admin === false || (!showMode && !showRefresh)) return nothing;
    const mode = overview.attributes.fetch_mode === "manual" ? "manual" : "automatic";
    const busy = this._manualRefreshInFlight || this._modeChangeInFlight;
    const cooldownActive = cooldown.backend > 0;
    const backendAllowsRefresh = typeof overview.attributes.manual_refresh_available === "boolean"
      ? overview.attributes.manual_refresh_available
      : !cooldownActive;
    const blocked = !backendAllowsRefresh;
    return html`<div class="controls" aria-label="${showMode ? this._text("fetchMode") : this._text("refreshNow")}">
      ${showMode ? html`<span class="control-label">${this._text("fetchMode")}</span>` : nothing}
      ${showMode ? html`<div class="mode-switch" role="group" aria-label="${this._text("fetchMode")}">
        <button class=${mode === "automatic" ? "selected" : ""} ?disabled=${busy || mode === "automatic"} @click=${() => this._setFetchMode(entryId, "automatic")}>${this._text("automatic")}</button>
        <button class=${mode === "manual" ? "selected" : ""} ?disabled=${busy || mode === "manual"} @click=${() => this._setFetchMode(entryId, "manual")}>${this._text("manual")}</button>
      </div>` : nothing}
      ${showRefresh && mode === "manual" ? html`<button class="refresh" ?disabled=${busy || blocked} @click=${() => this._manualRefresh(entryId)}>${this._manualRefreshInFlight ? this._text("refreshing") : cooldownActive && blocked ? this._cooldownLabel(cooldown.display) : blocked ? this._blockedRefreshLabel(overview) : this._text("refreshNow")}</button>` : nothing}
    </div>`;
  }

  private _providerStatus(overview: HassState, compact = false, enabled = true) {
    const cooldowns = overview.attributes.provider_cooldowns && typeof overview.attributes.provider_cooldowns === "object"
      ? overview.attributes.provider_cooldowns as Record<string, Record<string, unknown>> : {};
    const quotas = overview.attributes.provider_quotas && typeof overview.attributes.provider_quotas === "object"
      ? overview.attributes.provider_quotas as Record<string, Record<string, unknown>> : {};
    const availability = overview.attributes.provider_availability && typeof overview.attributes.provider_availability === "object"
      ? overview.attributes.provider_availability as Record<string, Record<string, unknown>> : {};
    const providers = Array.from(new Set([...Object.keys(cooldowns), ...Object.keys(quotas), ...Object.keys(availability)]));
    if (!enabled || !providers.length) return nothing;
    let activeCooldown = false;
    const rows = providers.map((provider) => {
      const cooldown = cooldowns[provider] ?? {};
      const quota = quotas[provider] ?? {};
      const providerAvailability = availability[provider] ?? {};
      const availabilityStatus = typeof providerAvailability.status === "string" ? providerAvailability.status : undefined;
      const cooldownSeconds = this._serverCooldownSeconds(cooldown);
      activeCooldown ||= cooldownSeconds > 0;
      const rawQuotas = quota.quotas && typeof quota.quotas === "object" ? quota.quotas as Record<string, Record<string, unknown>> : {};
      const cheap = rawQuotas.cheap;
      const remaining = cheap && Number.isInteger(cheap.remaining) ? Number(cheap.remaining) : undefined;
      const limit = cheap && Number.isInteger(cheap.limit) ? Number(cheap.limit) : undefined;
      const quotaText = quota.available === true && remaining !== undefined && limit !== undefined
        ? `${this._providerLabel(provider)} · ${remaining}/${limit} ${this._text("callsRemaining")}${quota.stale === true ? ` · ${this._text("quotaStale")}` : ""}`
        : `${this._providerLabel(provider)} · ${this._text("quotaUnavailable")}`;
      const availabilityText = availabilityStatus === "market_not_allowed"
        ? `${this._providerLabel(provider)} · ${this._text("marketNotAllowed")}`
        : availabilityStatus === "coverage_unknown"
          ? `${this._providerLabel(provider)} · ${this._text("coverageUnknown")}`
          : availabilityStatus === "quota_exhausted"
            ? `${this._providerLabel(provider)} · ${this._text("quotaExhausted")}`
          : availabilityStatus === "not_configured"
              ? `${this._providerLabel(provider)} · ${this._text("notConfigured")}`
              : availabilityStatus === "country_unknown"
                ? `${this._providerLabel(provider)} · ${this._text("countryUnknown")}`
                : availabilityStatus === "unsupported_country"
                  ? `${this._providerLabel(provider)} · ${this._text("unsupportedCountry")}`
              : quotaText;
      return html`<div class="secondary provider-status" role="status">
        ${cooldownSeconds > 0 ? html`${this._providerLabel(provider)} · ${this._text("cooldownActive")} · ${this._cooldownLabel(cooldownSeconds)}` : availabilityText}
      </div>`;
    });
    if (!activeCooldown && Number(overview.attributes.provider_cooldown_remaining) <= 0 && this._cooldownTimer !== undefined) {
      window.clearInterval(this._cooldownTimer);
      this._cooldownTimer = undefined;
    }
    const content = html`<div class="provider-status-list" aria-label="${this._text("providerStatus")}">${rows}</div>`;
    return compact
      ? html`<details class="diagnostics"><summary>${this._locale() === "en-US" ? "Diagnostics" : "Diagnose"}</summary>${content}</details>`
      : content;
  }

  private _serverCooldownSeconds(status: Record<string, unknown>): number {
    const until = typeof status.cooldown_until === "string" ? Date.parse(status.cooldown_until) : Number.NaN;
    const seconds = Number.isFinite(until)
      ? Math.max(0, Math.ceil((until - Date.now()) / 1000))
      : Number(status.remaining_seconds);
    const safe = Number.isFinite(seconds) && seconds > 0 ? Math.ceil(seconds) : 0;
    if (safe > 0 && this._cooldownTimer === undefined) this._cooldownTimer = window.setInterval(() => this.requestUpdate(), 1000);
    return safe;
  }

  private async _setFetchMode(entryId: string, mode: "automatic" | "manual") {
    if (!this._hass?.callService || this._modeChangeInFlight) return;
    this._modeChangeInFlight = true;
    try {
      await this._hass.callService("mobile_fuel_stations", "set_fetch_mode", { entry_id: entryId, fetch_mode: mode });
      this._controlError = undefined;
    } catch (error) {
      const message = error instanceof Error ? error.message : this._text("controlFailed");
      this._controlError = /cooldown/i.test(message) ? undefined : message;
    } finally {
      this._modeChangeInFlight = false;
      this.requestUpdate();
    }
  }

  private async _manualRefresh(entryId: string) {
    if (!this._hass?.callService || this._manualRefreshInFlight) return;
    this._manualRefreshInFlight = true;
    this.requestUpdate();
    try {
      await this._hass.callService("mobile_fuel_stations", "manual_refresh", { entry_id: entryId });
      this._controlError = undefined;
    } catch (error) {
      const message = error instanceof Error ? error.message : this._text("controlFailed");
      this._controlError = /cooldown/i.test(message) ? undefined : message;
    } finally {
      this._manualRefreshInFlight = false;
      this.requestUpdate();
    }
  }

  private _highlights(overview: HassState, visibleIds: string[]) {
    const highlights: Array<[string, HighlightStation]> = [];
    const perFuel = Object.entries((overview.attributes.cheapest_stations_by_fuel as Record<string, HighlightStation> | undefined) ?? {});
    const cheapest = perFuel.length ? perFuel.map(([fuel, station]) => [`${this._text("cheapest")} ${fuelLabel(fuel)}`, station] as [string, HighlightStation]) : [[this._text("cheapest"), overview.attributes.cheapest_station] as [string, HighlightStation | unknown]];
    for (const [label, value] of [[this._text("nearest"), overview.attributes.nearest_station], ...cheapest]) {
      if (value && typeof value === "object") highlights.push([String(label), value as HighlightStation]);
    }
    if (!highlights.length) return nothing;
    const merged = new Map<string, { labels: string[]; station: HighlightStation }>();
    highlights.forEach(([label, station], index) => {
      const stationId = text(station.station_id);
      const entityId = stationId ? visibleIds.find((id) => this._hass?.states[id]?.attributes.station_id === stationId) : undefined;
      const key = stationId ? `station:${stationId}` : entityId ? `entity:${entityId}` : `highlight:${index}`;
      const existing = merged.get(key);
      if (existing) existing.labels.push(label);
      else merged.set(key, { labels: [label], station });
    });
    return html`<div class="highlights">${Array.from(merged.values()).map(({ labels, station }) => this._highlight(labels.join(" · "), station, visibleIds))}</div>`;
  }

  private _highlight(label: string, station: HighlightStation, visibleIds: string[]) {
    const stationId = text(station.station_id);
    const entityId = stationId ? visibleIds.find((id) => this._hass?.states[id]?.attributes.station_id === stationId) : undefined;
    const name = text(station.station_name) ?? text(station.brand) ?? stationId ?? this._text("notFound");
    const brand = text(station.brand);
    const fuelPrice = station.fuel_prices?.[station.requested_fuel ?? station.fuel_type ?? ""] ?? station.price;
    const price = formatPrice(fuelPrice, this._locale(), text(station.currency) ?? "EUR") ?? this._text("noPrice");
    const distance = formatDistance(station.distance, this._locale());
    const providerEntity = stationId ? visibleIds.find((id) => this._hass?.states[id]?.attributes.station_id === stationId) : undefined;
    const provider = this._providerLabel(station.provider ?? (providerEntity ? this._hass?.states[providerEntity]?.attributes.provider : undefined));
    const navigationUrl = this._config?.navigation !== false ? buildNavigationUrl(station.latitude, station.longitude, this._config?.navigation_provider ?? "auto") : null;
    const address = [station.street && station.house_number ? `${station.street} ${station.house_number}` : text(station.street), [station.postcode, station.place].filter(Boolean).join(" ")].filter(Boolean).join(", ");
    return html`<div class="highlight${entityId ? " is-link" : ""}" role=${entityId ? "button" : nothing} tabindex=${entityId ? "0" : nothing} aria-label="${name}" @click=${entityId ? () => this._moreInfo(entityId) : undefined} @keydown=${entityId ? (event: KeyboardEvent) => this._keyActivate(event, entityId) : undefined}>
      ${this._brandLogo(brand, name)}
      <div><div class="highlight-label">${label}</div><div class="highlight-name">${name}${brand && shouldShowBrand(name, brand) ? html` <span class="secondary">(${brand})</span>` : nothing}</div>${address ? html`<div class="address">${address}</div>` : nothing}<div class="provider">${this._text("source")}: ${provider}</div></div>
      <div><div class="price">${price}</div>${distance ? html`<div class="meta">${distance}</div>` : nothing}</div>
      ${navigationUrl ? html`<a class="navigate" href=${navigationUrl} target="_blank" rel="noopener noreferrer" aria-label="${this._text("navigate")}" @click=${(event: Event) => event.stopPropagation()}><ha-icon icon="mdi:navigation" aria-hidden="true"></ha-icon></a>` : nothing}
    </div>`;
  }

  private _summary(overview: HassState, stations: Array<{ id: string; state: HassState }>, config?: CardConfig): string {
    const parts: string[] = [];
    const count = Number(overview.attributes.station_count);
    if (Number.isFinite(count) && config?.show_station_count !== false) parts.push(`${count} Tankstellen`);
    const radius = formatDistance(overview.attributes.radius, this._locale());
    if (radius && config?.show_radius !== false) parts.push(radius);
    const fuels = Array.isArray(overview.attributes.fuel_types) ? overview.attributes.fuel_types : [overview.attributes.fuel_type];
    const labels = fuels.map((fuel) => fuelLabel(fuel)).filter((fuel): fuel is string => Boolean(fuel));
    if (labels.length && config?.show_fuel_type !== false) parts.push(labels.join(", "));
    if (overview.attributes.last_successful_update && config?.show_last_updated !== false) {
      const date = new Date(String(overview.attributes.last_successful_update));
      if (!Number.isNaN(date.getTime())) parts.push(`${this._text("asOf")} ${new Intl.DateTimeFormat(this._locale(), { hour: "2-digit", minute: "2-digit" }).format(date)} (${this._relativeTime(date)})`);
    }
    if (config?.show_provider !== false) parts.push(`${this._text("source")}: ${this._providerSummary(stations.map(({ state }) => state.attributes.provider))}`);
    return parts.join(" · ");
  }

  private _relativeTime(date: Date): string {
    const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
    if (seconds < 60) return this._locale() === "en-US" ? "just now" : "gerade eben";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return this._locale() === "en-US" ? `${minutes}m ago` : `vor ${minutes} Min.`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return this._locale() === "en-US" ? `${hours}h ago` : `vor ${hours} Std.`;
    const days = Math.floor(hours / 24);
    return this._locale() === "en-US" ? `${days}d ago` : `vor ${days} Tg.`;
  }

  private _providerId(value: unknown): string | null {
    return typeof value === "string" && value.trim() ? value.trim().toLowerCase() : null;
  }

  private _providerLabel(value: unknown): string {
    const labels: Record<string, string> = {
      tankerkoenig: "Tankerkönig",
      petromap: "Petromap",
      nakordoni: "Nakordoni",
    };
    const id = this._providerId(value);
    return id ? labels[id] ?? id : this._text("unknownSource");
  }

  private _providerSummary(values: unknown[]): string {
    const providers = values.map((value) => this._providerId(value));
    const known = new Set(providers.filter((value): value is string => value !== null));
    if (known.size === 1 && providers.every((value) => value !== null)) return this._providerLabel([...known][0]);
    if (known.size === 0) return this._text("unknownSource");
    return this._text("multipleSources");
  }

  private _hasNakordoni(overview: HassState, stations: Array<{ id: string; state: HassState }>): boolean {
    return this._providerId(overview.attributes.provider) === "nakordoni"
      || stations.some(({ state }) => this._providerId(state.attributes.provider) === "nakordoni");
  }

  private _staleMessage(overview: HassState): string {
    const raw = overview.attributes.last_successful_update;
    const date = typeof raw === "string" ? new Date(raw) : undefined;
    const at = date && !Number.isNaN(date.getTime())
      ? ` · ${this._text("lastSuccessful")} ${new Intl.DateTimeFormat(this._locale(), { dateStyle: "short", timeStyle: "short" }).format(date)}`
      : "";
    const error = typeof overview.attributes.last_update_error_class === "string"
      ? ` (${overview.attributes.last_update_error_class})`
      : "";
    return `${this._text("stale")}${error}${at}`;
  }

  private _hasRefreshError(overview: HassState): boolean {
    const result = overview.attributes.last_update_result;
    return typeof result === "string" && ["provider_failed", "provider_auth_failed", "provider_rate_limited", "provider_transient_failure", "provider_response_error", "provider_quota_exhausted", "provider_permission_denied", "provider_unavailable", "network_timeout", "network_error", "provider_cooldown", "gps_unavailable"].includes(result);
  }

  private _refreshError(overview: HassState, cooldown: number): string {
    const error = text(overview.attributes.last_update_error_class);
    if (overview.attributes.last_update_result === "provider_cooldown" && cooldown > 0) {
      return this._cooldownLabel(cooldown);
    }
    const result = overview.attributes.last_update_result;
    const message = result === "gps_unavailable" ? this._text("locationMissing")
      : result === "provider_auth_failed" ? this._text("providerAuthFailed")
      : result === "provider_rate_limited" ? this._text("providerRateLimited")
      : result === "provider_quota_exhausted" ? this._text("providerQuotaExhausted")
      : result === "provider_response_error" ? this._text("providerResponseError")
      : result === "network_timeout" ? this._text("networkTimeout")
      : result === "network_error" ? this._text("networkError")
      : result === "provider_unavailable" ? this._text("providerUnavailable")
      : this._text("refreshFailed");
    return `${message}${error ? ` (${error})` : ""}`;
  }

  private _fallbackMessage(overview: HassState): string | null {
    const provider = text(overview.attributes.fallback_provider);
    if (overview.attributes.fallback_result === "success" && provider) {
      return `${this._text("fallbackUsed")}: ${this._providerLabel(provider)}`;
    }
    const reason = text(overview.attributes.fallback_skip_reason);
    if (reason?.includes("unknown_coverage") || reason?.includes("provider_disabled")) {
      return this._text("fallbackUnavailable");
    }
    return null;
  }

  private _cooldownState(overview: HassState): { backend: number; display: number } {
    const retry = overview.attributes.manual_refresh_retry_seconds;
    const raw = Number(retry !== undefined
      ? retry
      : overview.attributes.provider_cooldown_remaining);
    const backend = Number.isFinite(raw) && raw > 0 ? Math.ceil(raw) : 0;
    if (backend !== this._cooldownObservedSeconds) {
      this._cooldownObservedSeconds = backend;
      this._cooldownObservedAt = Date.now();
    }
    if (backend > 0 && this._cooldownTimer === undefined) {
      this._cooldownTimer = window.setInterval(() => this.requestUpdate(), 1000);
    } else if (backend === 0 && this._cooldownTimer !== undefined) {
      window.clearInterval(this._cooldownTimer);
      this._cooldownTimer = undefined;
    }
    const elapsed = this._cooldownObservedAt ? Math.floor((Date.now() - this._cooldownObservedAt) / 1000) : 0;
    return { backend, display: Math.max(0, backend - elapsed) };
  }

  private _blockedRefreshLabel(overview: HassState): string {
    const reason = text(overview.attributes.manual_refresh_blocked_reason) ?? "";
    if (reason.includes("country_unknown")) return this._text("countryUnknown");
    if (reason.includes("unsupported_country")) return this._text("unsupportedCountry");
    if (reason.includes("coverage_unknown")) return this._text("coverageUnknown");
    if (reason.includes("market_not_allowed")) return this._text("marketNotAllowed");
    if (reason.includes("quota_exhausted")) return this._text("quotaExhausted");
    return this._text("noProviderAvailable");
  }

  private _cooldownLabel(seconds: number): string {
    const safe = Math.max(0, Math.ceil(seconds));
    return `${this._text("retryIn")} ${Math.floor(safe / 60)}:${String(safe % 60).padStart(2, "0")}`;
  }

  private _featuredStation(station: StationPriority) {
    const { id, state, isNearest, isCheapest } = station;
    const a = state.attributes;
    const name = text(a.station_name) ?? text(a.name) ?? id;
    const brand = text(a.brand);
    const distance = formatDistance(a.distance, this._locale());
    const fuelPrices = a.fuel_prices && typeof a.fuel_prices === "object" ? a.fuel_prices as Record<string, unknown> : undefined;
    const selectedFuel = this._config?.sort_fuel ?? text(a.requested_fuel) ?? text(a.fuel_type) ?? (fuelPrices ? Object.keys(fuelPrices)[0] : undefined);
    const selectedPrice = selectedFuel && fuelPrices ? fuelPrices[selectedFuel] : state.state;
    const price = formatPrice(selectedPrice, this._locale(), text(a.currency) ?? "EUR") ?? this._text("noPrice");
    const badges = this._config?.show_badges !== false ? this._stationBadges(isNearest, isCheapest, false) : nothing;
    const navigationUrl = this._config?.navigation !== false ? buildNavigationUrl(a.latitude, a.longitude, this._config?.navigation_provider ?? "auto") : null;
    const navigation = navigationUrl ? html`<a class="navigate" href=${navigationUrl} target="_blank" rel="noopener noreferrer" aria-label="${this._text("navigate")}" @click=${(event: Event) => event.stopPropagation()}><ha-icon icon="mdi:navigation" aria-hidden="true"></ha-icon></a>` : nothing;
    const label = `${name}, ${this._locale() === "en-US" ? "price" : "Preis"} ${price}${distance ? `, ${distance}` : ""}`;
    const featuredClass = `featured-station ${this._config?.show_brand_logos === false ? "no-logo" : ""} ${navigationUrl ? "" : "no-navigation"}`.trim();
    return html`<article class="${featuredClass}" role="button" tabindex="0" aria-label="${label}" @click=${() => this._moreInfo(id)} @keydown=${(event: KeyboardEvent) => this._keyActivate(event, id)}>
      <div class="featured-top">${this._brandLogo(brand, name)}<div class="featured-main"><div class="featured-name" title=${name}>${name}</div>${badges}</div>${navigation}</div>
      <div class="featured-values">${this._config?.show_prices !== false ? html`<span class="price">${price}</span>` : nothing}${this._config?.show_distance !== false && distance ? html`<span class="meta">${distance}</span>` : nothing}</div>
    </article>`;
  }

  private _station(station: StationPriority, compact = false) {
    const { id, state, isNearest, isCheapest } = station;
    const a = state.attributes;
    const name = text(a.station_name) ?? text(a.name) ?? id;
    const brand = text(a.brand);
    const provider = this._providerLabel(a.provider);
    const fuelPrices = a.fuel_prices && typeof a.fuel_prices === "object" ? a.fuel_prices as Record<string, unknown> : undefined;
    const addressParts = [a.street && a.house_number ? `${a.street} ${a.house_number}` : text(a.street), [a.postcode, a.place].filter(Boolean).join(" ")].filter(Boolean);
    const address = addressParts.join(", ");
    const priceRows = fuelPrices ? Object.entries(fuelPrices).map(([fuel, value]) => ({ fuel: fuelLabel(fuel) ?? fuel, value: formatPrice(value, this._locale(), text(a.currency) ?? "EUR"), fallback: Boolean((a.fuel_fallbacks as Record<string, boolean> | undefined)?.[fuel]) })) : [{ fuel: fuelLabel(a.fuel_type ?? a.requested_fuel) ?? "", value: formatPrice(state.state, this._locale(), text(a.currency) ?? "EUR"), fallback: Boolean(a.fallback_used) }];
    const distance = formatDistance(a.distance, this._locale());
    const open = typeof a.is_open === "boolean" ? a.is_open : undefined;
    const status = open === undefined ? null : open ? "Geöffnet" : "Geschlossen";
    const freshness = a.price_stale === true ? this._text("stale") : a.price_age_hours != null ? `${this._text("priceAge")} ${a.price_age_hours}h` : null;
    const config = this._config ?? DEFAULT_CARD_CONFIG;
    const showName = config.show_name !== false;
    const showAddress = config.show_address !== false;
    const showStatus = config.show_status !== false;
    const showDistance = config.show_distance !== false;
    const showPrices = config.show_prices !== false;
    const showFuelLabels = config.show_fuel_labels !== false;
    const custom = config.display_mode === "custom";
    const showProvider = !compact && !custom && config.show_provider_row !== false;
    const showBadges = config.show_badges !== false;
    const label = `${name}, ${priceRows.map((row) => `${row.fuel} ${row.value ?? this._text("noPrice")}`).join(", ")}`;
    const navigationUrl = this._config?.navigation !== false ? buildNavigationUrl(a.latitude, a.longitude, this._config?.navigation_provider ?? "auto") : null;
    const badges = showBadges ? this._stationBadges(isNearest, isCheapest, compact) : nothing;
    const fuelMarkup = showPrices ? priceRows.map((row) => html`<div class="fuel-price">${showFuelLabels ? html`<span>${row.fuel}${row.fallback ? html` <span class="secondary">(${this._text("fallback")})</span>` : nothing}</span>` : nothing}<strong>${row.value ?? this._text("noPrice")}</strong></div>`) : nothing;
    const navigation = navigationUrl ? html`<a class="navigate" href=${navigationUrl} target="_blank" rel="noopener noreferrer" aria-label="${this._text("navigate")}" @click=${(event: Event) => event.stopPropagation()}><ha-icon icon="mdi:navigation" aria-hidden="true"></ha-icon></a>` : nothing;
    const nameClass = config.name_mode === "short" ? "name short" : "name";
    const showPricesColumn = showPrices || (!custom && !compact && showDistance && Boolean(distance));
    const stationClass = [compact ? "compact-station" : "", custom ? "custom-station" : "", showAddress ? "" : "no-address", config.show_brand_logos === false ? "no-logo" : "", navigationUrl ? "" : "no-navigation", showPricesColumn ? "" : "no-prices"].filter(Boolean).join(" ");
    const nameMarkup = showName ? html`<div class=${nameClass} title=${name}>${name}${brand && shouldShowBrand(name, brand) ? html` <span class="secondary">(${brand})</span>` : nothing}${badges}</div>` : badges;
    if (compact) {
      return html`<div class="station ${stationClass}" role="button" tabindex="0" aria-label="${label}" @click=${() => this._moreInfo(id)} @keydown=${(event: KeyboardEvent) => this._keyActivate(event, id)}>
        ${this._brandLogo(brand, name)}
        <div class="station-main">
          ${nameMarkup}
          ${showAddress && address ? html`<div class="address" title=${address}>${address}</div>` : nothing}
          <div class="station-meta" aria-label="${[status ? (open ? this._text("open") : this._text("closed")) : null, distance].filter(Boolean).join(", ")}">
            ${showStatus && status ? html`<span class=${open ? "open" : "closed"}>${open ? this._text("open") : this._text("closed")}</span>` : nothing}
            ${showDistance && distance ? html`<span class="meta">${distance}</span>` : nothing}
          </div>
        </div>
        ${showPricesColumn ? html`<div class="prices">${fuelMarkup}</div>` : nothing}
        ${navigation}
      </div>`;
    }
    const detailMeta = html`${showStatus && status ? html`<span class=${open ? "open" : "closed"}>${open ? this._text("open") : this._text("closed")}</span>` : nothing}${showDistance && distance ? html`<span class="distance">${distance}</span>` : nothing}${config.show_provider_row !== false ? html`<span>${this._text("source")}: ${provider}</span>` : nothing}${freshness ? html`<span>${freshness}</span>` : nothing}`;
    const hasDetailMeta = Boolean((showStatus && status) || (showDistance && distance) || config.show_provider_row !== false || freshness);
    const hasPrimary = showName || showBadges || showPrices;
    if (custom) {
      return html`<div class="station ${stationClass}" role="button" tabindex="0" aria-label="${label}" @click=${() => this._moreInfo(id)} @keydown=${(event: KeyboardEvent) => this._keyActivate(event, id)}>
        ${this._brandLogo(brand, name)}
        <div class="station-main">
          ${hasPrimary ? html`<div class="custom-primary">${nameMarkup}${showPrices ? html`<div class="custom-prices">${fuelMarkup}</div>` : nothing}</div>` : nothing}
          ${showAddress && address ? html`<div class="address" title=${address}>${address}</div>` : nothing}
          ${hasDetailMeta ? html`<div class="detail-meta">${detailMeta}</div>` : nothing}
        </div>
        ${navigation}
      </div>`;
    }
    return html`<div class="station ${stationClass}" role="button" tabindex="0" aria-label="${label}" @click=${() => this._moreInfo(id)} @keydown=${(event: KeyboardEvent) => this._keyActivate(event, id)}>
      ${this._brandLogo(brand, name)}
      <div>${nameMarkup}${showAddress && address ? html`<div class="address" title=${address}>${address}</div>` : nothing}${custom ? html`<div class="detail-meta">${detailMeta}</div>` : html`${showProvider ? html`<div class="provider">${this._text("source")}: ${provider}</div>` : nothing}${showStatus && status ? html`<div class=${open ? "open" : "closed"}>${open ? this._text("open") : this._text("closed")}</div>` : nothing}${freshness ? html`<div class="secondary">${freshness}</div>` : nothing}`}</div>
      ${showPricesColumn ? html`<div class="prices">${fuelMarkup}${!custom && showDistance && distance ? html`<div class="meta">${distance}</div>` : nothing}</div>` : nothing}
      ${navigation}
    </div>`;
  }

  private _stationBadges(isNearest: boolean, isCheapest: boolean, compact: boolean) {
    if (!isNearest && !isCheapest) return nothing;
    return html`<span class="station-badges" aria-label="${this._locale() === "en-US" ? "Station highlights" : "Tankstellenkennzeichnungen"}">
      ${isNearest ? html`<span class="station-badge" title="${this._text("nearest")}"><ha-icon icon="mdi:map-marker-radius" aria-hidden="true"></ha-icon>${compact ? html`<span class="sr-only">${this._text("nearest")}</span>` : this._text("nearest")}</span>` : nothing}
      ${isCheapest ? html`<span class="station-badge cheapest" title="${this._text("cheapest")}"><ha-icon icon="mdi:tag-heart" aria-hidden="true"></ha-icon>${compact ? html`<span class="sr-only">${this._text("cheapest")}</span>` : this._text("cheapest")}</span>` : nothing}
    </span>`;
  }

  private _message(message: string) { return html`<ha-card><div class="message">${message}</div></ha-card>`; }
  private _brandLogo(brand: unknown, alt: string) {
    const config = this._config;
    if (!config || config.show_brand_logos === false) return nothing;
    const url = buildBrandLogoUrl(brand, config.logo_path, alt);
    const cacheKey = url ?? "fallback";
    if (!url || this._failedBrandLogos.has(cacheKey)) return html`<ha-icon class="icon" icon="mdi:gas-station" aria-label="${this._text("unknownBrand")}"></ha-icon>`;
    return html`<span class="brand-logo"><img src=${url} alt="${alt} ${this._text("brandLogo")}" @error=${() => { this._failedBrandLogos.add(cacheKey); this.requestUpdate(); }}></span>`;
  }
  private _locale(): string { return this._hass?.locale?.language?.toLowerCase().startsWith("en") ? "en-US" : "de-DE"; }
  private _text(key: "title" | "open" | "closed" | "noPrice" | "none" | "asOf" | "navigate" | "unavailable" | "notFound" | "selectEntity" | "nearest" | "cheapest" | "stale" | "lastSuccessful" | "priceAge" | "fallback" | "fallbackUsed" | "fallbackUnavailable" | "source" | "unknownSource" | "multipleSources" | "unknownBrand" | "brandLogo" | "fetchMode" | "automatic" | "manual" | "refreshNow" | "refreshing" | "refreshFailed" | "cooldownActive" | "retryIn" | "providerPricesStale" | "locationMissing" | "providerAuthFailed" | "providerRateLimited" | "providerQuotaExhausted" | "providerResponseError" | "networkTimeout" | "networkError" | "providerUnavailable" | "controlFailed" | "noProviderAvailable" | "providerStatus" | "callsRemaining" | "quotaStale" | "quotaUnavailable" | "marketNotAllowed" | "coverageUnknown" | "quotaExhausted" | "notConfigured" | "countryUnknown" | "unsupportedCountry"): string {
    const english = this._locale() === "en-US";
    const values = english ? { title: "Nearby fuel stations", open: "Open", closed: "Closed", noPrice: "Price unavailable", none: "No fuel stations found", asOf: "As of", navigate: "Navigate", unavailable: "Fuel stations currently unavailable", notFound: "Overview entity not found", selectEntity: "Select an overview entity", nearest: "Nearest", cheapest: "Cheapest", stale: "Data stale", lastSuccessful: "last successful update", priceAge: "Confirmed", fallback: "E5 instead of E10", fallbackUsed: "Fallback provider used", fallbackUnavailable: "Fallback provider unavailable: market permission missing", source: "Source", unknownSource: "Source unknown", multipleSources: "Multiple data sources", unknownBrand: "Unknown station brand", brandLogo: "logo", fetchMode: "Fetch mode", automatic: "Automatic", manual: "Manual", refreshNow: "Fetch now", refreshing: "Fetching…", refreshFailed: "Station refresh failed", cooldownActive: "Provider cooldown active", retryIn: "Retry in", providerPricesStale: "Provider prices are stale", locationMissing: "Location data unavailable", providerAuthFailed: "Provider authentication failed", providerRateLimited: "Provider rate limit reached", providerQuotaExhausted: "Provider quota exhausted", providerResponseError: "Provider returned an invalid response", networkTimeout: "Provider request timed out", networkError: "Provider network error", providerUnavailable: "Provider temporarily unavailable", controlFailed: "Station control failed", noProviderAvailable: "No provider available", providerStatus: "Provider status", callsRemaining: "calls remaining", quotaStale: "quota data stale", quotaUnavailable: "quota unavailable", marketNotAllowed: "market permission not confirmed", coverageUnknown: "market coverage unknown", quotaExhausted: "API quota exhausted", notConfigured: "provider not configured", countryUnknown: "country not confirmed", unsupportedCountry: "country not supported" } : { title: "Tankstellen in der Nähe", open: "Geöffnet", closed: "Geschlossen", noPrice: "Preis nicht verfügbar", none: "Keine Tankstellen gefunden", asOf: "Stand", navigate: "Navigieren", unavailable: "Tankstellen derzeit nicht verfügbar", notFound: "Overview entity not found", selectEntity: "Bitte eine Overview-Entity auswählen", nearest: "Nächste", cheapest: "Günstigste", stale: "Daten veraltet", lastSuccessful: "letzte erfolgreiche Aktualisierung", priceAge: "Bestätigt", fallback: "E5 statt E10", fallbackUsed: "Ersatzanbieter verwendet", fallbackUnavailable: "Ersatzanbieter nicht verfügbar: Marktberechtigung fehlt", source: "Quelle", unknownSource: "Quelle unbekannt", multipleSources: "Mehrere Datenquellen", unknownBrand: "Unbekannte Tankstellenmarke", brandLogo: "Logo", fetchMode: "Abrufmodus", automatic: "Automatisch", manual: "Manuell", refreshNow: "Jetzt abrufen", refreshing: "Wird abgerufen…", refreshFailed: "Tankstellenabruf fehlgeschlagen", cooldownActive: "Provider-Cooldown aktiv", retryIn: "Erneut abrufen in", providerPricesStale: "Providerpreise sind veraltet", locationMissing: "Standortdaten fehlen", providerAuthFailed: "Provider-Authentifizierung fehlgeschlagen", providerRateLimited: "Provider-Limit erreicht", providerQuotaExhausted: "API-Kontingent erschöpft", providerResponseError: "Provider-Antwort konnte nicht verarbeitet werden", networkTimeout: "Netzwerk-/Timeout-Fehler beim Provider", networkError: "Netzwerkfehler beim Provider", providerUnavailable: "Provider ist vorübergehend nicht verfügbar", controlFailed: "Tankstellensteuerung fehlgeschlagen", noProviderAvailable: "Kein Provider verfügbar", providerStatus: "Providerstatus", callsRemaining: "Aufrufe verbleibend", quotaStale: "Kontingentdaten veraltet", quotaUnavailable: "Kontingent nicht verfügbar", marketNotAllowed: "Marktberechtigung nicht bestätigt", coverageUnknown: "Marktabdeckung unbekannt", quotaExhausted: "API-Kontingent erschöpft", notConfigured: "Provider nicht konfiguriert", countryUnknown: "Land nicht bestätigt", unsupportedCountry: "Land nicht unterstützt" };
    return values[key];
  }
  private _keyActivate(event: KeyboardEvent, id: string) { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); this._moreInfo(id); } }
  private _moreInfo(entityId: string) { this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId } })); }
}

class MobileFuelStationsCardEditor extends LitElement {
  static styles = css`
    :host { display: block; }
    label { display: block; color: var(--primary-text-color); margin: 8px 0; }
    .field { display: block; }
    select, input:not([type="checkbox"]) { box-sizing: border-box; width: 100%; padding: 8px; color: var(--primary-text-color); background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 4px; }
    input[type="checkbox"] { width: auto; margin: 0; accent-color: var(--primary-color); }
    .option { display: flex; align-items: center; gap: 8px; min-height: 32px; margin: 3px 0; cursor: pointer; }
    .option span { min-width: 0; }
    fieldset { margin: 12px 0; padding: 8px 12px 10px; border: 1px solid var(--divider-color); border-radius: 8px; }
    legend { padding: 0 4px; color: var(--secondary-text-color); font-weight: 600; }
    .row { margin-top: 12px; }
  `;
  private _config: CardConfig = normalizeCardConfig({ display_mode: "compact" });
  private _hass?: Hass;
  setConfig(config: CardConfig): void { this._config = normalizeCardConfig(config); this.requestUpdate(); }
  set hass(value: Hass) { this._hass = value; this.requestUpdate(); }
  protected render() {
    const entities = Object.entries(this._hass?.states ?? {}).filter(([id, value]) => this._isOverview(id, value));
    const selected = this._hass?.states[this._config.entity ?? ""];
    const fuelTypes = Array.from(new Set((Array.isArray(selected?.attributes.fuel_types) ? selected?.attributes.fuel_types : [selected?.attributes.fuel_type]).filter((fuel): fuel is string => typeof fuel === "string" && Boolean(fuel.trim()))));
    const mode = html`<div class="row"><label class="field">${this._text("displayMode")}<select .value=${this._config.display_mode ?? "detailed"} @change=${(event: Event) => this._changeDisplayMode(event)}><option value="compact">${this._text("compact")}</option><option value="detailed">${this._text("detailed")}</option><option value="custom">${this._text("custom")}</option></select></label></div>`;
    const custom = this._config.display_mode === "custom";
    const customOptions = custom ? html`
      <fieldset><legend>${this._text("customLayout")}</legend>
        <label class="field">${this._text("layout")}<select .value=${this._config.custom_layout ?? "list"} @change=${(event: Event) => this._changeCustomLayout(event)}><option value="list">${this._text("simpleList")}</option><option value="highlights_list">${this._text("highlightsList")}</option><option value="configured_list">${this._text("configuredList")}</option></select></label>
        <label class="field">${this._text("sortMode")}<select .value=${this._config.sort_mode ?? "distance"} @change=${(event: Event) => this._changeSortMode(event)}><option value="distance">${this._text("distanceSort")}</option><option value="price">${this._text("priceSort")}</option></select></label>
        <label class="field">${this._text("sortFuel")}<select .value=${this._config.sort_fuel ?? fuelTypes[0] ?? "diesel"} @change=${(event: Event) => this._changeSortFuel(event)}>${(fuelTypes.length ? fuelTypes : ["diesel"]).map((fuel) => html`<option value=${fuel}>${fuelLabel(fuel) ?? fuel}</option>`)}</select></label>
        <label class="field">${this._text("visibleCount")}<input type="number" min="0" step="1" .value=${String(this._config.visible_station_count ?? 0)} @change=${(event: Event) => this._changeNumber(event, "visible_station_count")}></label>
        <label class="field">${this._text("title")}<input .value=${this._config.title ?? ""} placeholder=${this._config.title ? "" : "Standard: Tankstellen in der Nähe / Default: Nearby fuel stations"} @change=${(event: Event) => this._changeText(event, "title")}></label>
      </fieldset>
      <fieldset><legend>${this._text("headerFields")}</legend>${this._checkbox("show_title", "showTitle")}${this._checkbox("show_station_count", "showCount")}${this._checkbox("show_radius", "showRadius")}${this._checkbox("show_fuel_type", "showFuel")}${this._checkbox("show_last_updated", "showUpdated")}${this._checkbox("show_provider", "showProvider")}${this._checkbox("show_fetch_mode", "showFetchMode")}${this._checkbox("show_diagnostics", "showDiagnostics")}${this._checkbox("show_refresh", "showRefresh")}</fieldset>
      <fieldset><legend>${this._text("stationFields")}</legend>${this._checkbox("show_brand_logos", "brandLogos")}${this._checkbox("show_name", "stationName")}${this._checkbox("show_address", "address")}${this._checkbox("show_status", "status")}${this._checkbox("show_distance", "distance")}${this._checkbox("show_prices", "prices")}${this._checkbox("show_fuel_labels", "fuelLabels")}${this._checkbox("show_provider_row", "providerRow")}${this._checkbox("show_badges", "badges")}
        <label class="field">${this._text("nameMode")}<select .value=${this._config.name_mode ?? "full"} @change=${(event: Event) => this._changeNameMode(event)}><option value="full">${this._text("fullName")}</option><option value="short">${this._text("shortName")}</option></select></label>
        <label class="field">${this._text("density")}<select .value=${this._config.density ?? "normal"} @change=${(event: Event) => this._changeDensity(event)}><option value="normal">${this._text("normalSpacing")}</option><option value="compact">${this._text("compactSpacing")}</option></select></label>${this._checkbox("show_dividers", "dividers")}
      </fieldset>` : nothing;
    return html`${mode}<label class="field">${this._text("entity")}<select .value=${this._config.entity ?? ""} @change=${(event: Event) => this._changeEntity(event)}><option value="">${entities.length ? this._text("choose") : this._text("none")}</option>${entities.map(([id, value]) => html`<option value=${id}>${value?.attributes.friendly_name ?? id}</option>`)}</select></label>${customOptions}<fieldset><legend>${this._text("navigationSection")}</legend><label class="option"><input type="checkbox" .checked=${this._config.navigation !== false} @change=${(event: Event) => this._changeNavigation(event)}><span>${this._text("navigation")}</span></label><label class="field">${this._text("provider")}<select .value=${this._config.navigation_provider ?? "auto"} .disabled=${this._config.navigation === false} @change=${(event: Event) => this._changeProvider(event)}><option value="auto">${this._text("auto")}</option><option value="apple">${this._text("apple")}</option><option value="google">${this._text("google")}</option><option value="waze">${this._text("waze")}</option></select></label></fieldset>${custom ? nothing : html`<div class="row"><label class="option"><input type="checkbox" .checked=${this._config.show_brand_logos !== false} @change=${(event: Event) => this._changeBrandLogos(event)}><span>${this._text("brandLogos")}</span></label><label class="field">${this._text("logoPath")}<input .value=${this._config.logo_path ?? DEFAULT_LOGO_PATH} @change=${(event: Event) => this._changeLogoPath(event)}></label></div>`}`;
  }
  private _isOverview(id: string, value: HassState | undefined): boolean { return isOverviewEntity(id, value); }
  private _changeEntity(event: Event) { this._configChanged({ ...this._config, entity: (event.target as HTMLSelectElement).value }); }
  private _changeNavigation(event: Event) { this._configChanged({ ...this._config, navigation: (event.target as HTMLInputElement).checked }); }
  private _changeProvider(event: Event) { this._configChanged({ ...this._config, navigation_provider: (event.target as HTMLSelectElement).value as NavigationProvider }); }
  private _changeDisplayMode(event: Event) { this._configChanged({ ...this._config, display_mode: (event.target as HTMLSelectElement).value as CardDisplayMode }); }
  private _changeCustomLayout(event: Event) { this._configChanged({ ...this._config, custom_layout: (event.target as HTMLSelectElement).value as CustomLayout }); }
  private _changeSortMode(event: Event) { this._configChanged({ ...this._config, sort_mode: (event.target as HTMLSelectElement).value as CardSortMode }); }
  private _changeSortFuel(event: Event) { this._configChanged({ ...this._config, sort_fuel: (event.target as HTMLSelectElement).value }); }
  private _changeNumber(event: Event, key: "visible_station_count") { this._configChanged({ ...this._config, [key]: Math.max(0, Number((event.target as HTMLInputElement).value) || 0) }); }
  private _changeText(event: Event, key: "title") { this._configChanged({ ...this._config, [key]: (event.target as HTMLInputElement).value }); }
  private _changeNameMode(event: Event) { this._configChanged({ ...this._config, name_mode: (event.target as HTMLSelectElement).value as "full" | "short" }); }
  private _changeDensity(event: Event) { this._configChanged({ ...this._config, density: (event.target as HTMLSelectElement).value as CardDensity }); }
  private _checkbox(key: keyof CardConfig, labelKey: string) { const checked = this._config[key] !== false && typeof this._config[key] !== "string"; return html`<label class="option"><input type="checkbox" .checked=${checked} @change=${(event: Event) => this._changeBoolean(event, key)}><span>${this._text(labelKey as Parameters<MobileFuelStationsCardEditor["_text"]>[0])}</span></label>`; }
  private _changeBoolean(event: Event, key: keyof CardConfig) { this._configChanged({ ...this._config, [key]: (event.target as HTMLInputElement).checked }); }
  private _changeBrandLogos(event: Event) { this._configChanged({ ...this._config, show_brand_logos: (event.target as HTMLInputElement).checked }); }
  private _changeLogoPath(event: Event) { this._configChanged({ ...this._config, logo_path: (event.target as HTMLInputElement).value }); }
  private _configChanged(config: CardConfig) { this._config = config; this.dispatchEvent(new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config } })); }
  private _text(key: "entity" | "choose" | "none" | "navigation" | "navigationSection" | "provider" | "auto" | "apple" | "google" | "waze" | "selectEntity" | "brandLogos" | "logoPath" | "displayMode" | "compact" | "detailed" | "custom" | "customLayout" | "layout" | "simpleList" | "highlightsList" | "configuredList" | "sortMode" | "distanceSort" | "priceSort" | "sortFuel" | "visibleCount" | "title" | "headerFields" | "stationFields" | "showTitle" | "showCount" | "showRadius" | "showFuel" | "showUpdated" | "showProvider" | "showFetchMode" | "showDiagnostics" | "showRefresh" | "stationName" | "address" | "status" | "distance" | "prices" | "fuelLabels" | "providerRow" | "badges" | "nameMode" | "fullName" | "shortName" | "density" | "normalSpacing" | "compactSpacing" | "dividers"): string { return this._hass?.locale?.language?.toLowerCase().startsWith("en") ? { entity: "Overview entity", choose: "Select an entity", none: "No overview sensors found", navigation: "Show navigation", navigationSection: "Navigation", provider: "Navigation provider", auto: "Automatic", apple: "Apple Maps", google: "Google Maps", waze: "Waze", selectEntity: "Select an overview entity", brandLogos: "Show brand logos", logoPath: "Logo path", displayMode: "Display mode", compact: "Compact", detailed: "Detailed", custom: "Individual", customLayout: "Individual layout", layout: "Layout", simpleList: "Simple list", highlightsList: "Highlights + list", configuredList: "Configured list", sortMode: "Remaining station sort", distanceSort: "Distance — nearest first", priceSort: "Fuel price — cheapest first", sortFuel: "Price sorting fuel", visibleCount: "Visible stations (0 = all)", title: "Card title", headerFields: "Header fields", stationFields: "Station fields", showTitle: "Show title", showCount: "Show station count", showRadius: "Show radius", showFuel: "Show fuel type", showUpdated: "Show last update", showProvider: "Show provider", showFetchMode: "Show fetch-mode control", showDiagnostics: "Show diagnostics", showRefresh: "Show refresh button", stationName: "Show station name", address: "Show address", status: "Show opening status", distance: "Show distance", prices: "Show prices", fuelLabels: "Show fuel labels", providerRow: "Show provider per station", badges: "Show nearest/cheapest labels", nameMode: "Name length", fullName: "Full name", shortName: "Short / ellipsis", density: "Row spacing", normalSpacing: "Normal", compactSpacing: "Compact", dividers: "Show dividers" }[key] : { entity: "Overview-Entity", choose: "Bitte auswählen", none: "Keine Overview-Sensoren gefunden", navigation: "Navigation anzeigen", navigationSection: "Navigation", provider: "Navigationsanbieter", auto: "Automatisch", apple: "Apple Karten", google: "Google Maps", waze: "Waze", selectEntity: "Bitte eine Overview-Entity auswählen", brandLogos: "Markenlogos anzeigen", logoPath: "Logo-Pfad", displayMode: "Darstellung", compact: "Kompakt", detailed: "Ausführlich", custom: "Individuell", customLayout: "Individuelles Layout", layout: "Layout", simpleList: "Einfache Liste", highlightsList: "Kacheln + Liste", configuredList: "Konfigurierte Liste", sortMode: "Sortierung der übrigen Tankstellen", distanceSort: "Entfernung – nächste zuerst", priceSort: "Kraftstoffpreis – günstigste zuerst", sortFuel: "Kraftstoff für Preissortierung", visibleCount: "Sichtbare Tankstellen (0 = alle)", title: "Kartentitel", headerFields: "Kopfbereich", stationFields: "Tankstellenfelder", showTitle: "Titel anzeigen", showCount: "Tankstellenanzahl anzeigen", showRadius: "Radius anzeigen", showFuel: "Kraftstoffart anzeigen", showUpdated: "Letzte Aktualisierung anzeigen", showProvider: "Provider anzeigen", showFetchMode: "Abrufmodus anzeigen", showDiagnostics: "Diagnosebereich anzeigen", showRefresh: "Aktualisieren anzeigen", stationName: "Tankstellenname anzeigen", address: "Adresse anzeigen", status: "Öffnungsstatus anzeigen", distance: "Entfernung anzeigen", prices: "Preise anzeigen", fuelLabels: "Kraftstoffbezeichnungen anzeigen", providerRow: "Provider je Tankstelle anzeigen", badges: "Nächste/Günstigste anzeigen", nameMode: "Namenslänge", fullName: "Vollständiger Name", shortName: "Kurz / Ellipsis", density: "Zeilenabstand", normalSpacing: "Normal", compactSpacing: "Kompakt", dividers: "Trennlinien anzeigen" }[key]; }
}

function registerCustomElements(): void {
  // HA can replace the registry after an early extra_module_url import.  The
  // one-shot load hook makes the registration visible in the final registry
  // without polling, reloading the page, or defining an element twice.
  if (!customElements.get("mobile-fuel-stations-card")) {
    customElements.define("mobile-fuel-stations-card", MobileFuelStationsCard);
  }
  if (!customElements.get("mobile-fuel-stations-card-editor")) {
    customElements.define("mobile-fuel-stations-card-editor", MobileFuelStationsCardEditor);
  }
}

registerCustomElements();
if (document.readyState === "loading") {
  window.addEventListener("load", registerCustomElements, { once: true });
}

declare global { interface Window { customCards?: Array<Record<string, unknown>>; } }
window.customCards = window.customCards ?? [];
if (!window.customCards.some((card) => card.type === "mobile-fuel-stations-card")) {
  window.customCards.push({ type: "mobile-fuel-stations-card", name: "Mobile Fuel Stations", description: "Nearby fuel stations from the Mobile Fuel Stations integration", getEntitySuggestion: (hass: Hass, entityId: string) => isOverviewEntity(entityId, hass.states[entityId]) ? { config: { type: "custom:mobile-fuel-stations-card", entity: entityId } } : null });
}
