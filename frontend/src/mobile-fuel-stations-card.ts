import { LitElement, css, html, nothing } from "lit";

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
export type CardConfig = {
  type?: string;
  entity?: string;
  navigation?: boolean;
  navigation_provider?: NavigationProvider;
  show_brand_logos?: boolean;
  logo_path?: string;
};

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
    .stations { grid-template-columns: minmax(0, 1fr); }
    @container (min-width: 600px) {
      .highlights { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .header { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
      .summary { margin-top: 0; }
      .station { grid-template-columns: 32px minmax(12rem, 1fr) minmax(8rem, auto) auto; }
    }
    @container (max-width: 599px) {
      ha-card { padding: 12px; }
      .station { grid-template-columns: 26px minmax(0, 1fr) auto; gap: 6px; }
      .station .prices { grid-column: 2; grid-row: 2; text-align: left; }
      .fuel-price { justify-content: flex-start; gap: 4px; }
      .station .navigate { grid-column: 3; grid-row: 1 / span 2; align-self: center; }
      .highlight { grid-template-columns: 26px minmax(0, 1fr) auto auto; gap: 6px; }
      .highlight .navigate { grid-column: auto; }
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
      this._config = { ...(config ?? {}), type: config?.type ?? "custom:mobile-fuel-stations-card", navigation: config?.navigation !== false, navigation_provider: config?.navigation_provider ?? "auto", show_brand_logos: config?.show_brand_logos !== false, logo_path: config?.logo_path ?? DEFAULT_LOGO_PATH };
      this._configError = this._text("selectEntity");
      this.requestUpdate();
      return;
    }
    this._config = { ...config, type: config.type ?? "custom:mobile-fuel-stations-card", entity: config.entity, navigation: config.navigation !== false, navigation_provider: config.navigation_provider ?? "auto", show_brand_logos: config.show_brand_logos !== false, logo_path: config.logo_path ?? DEFAULT_LOGO_PATH };
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
    return entity ? { entity, navigation: true } : { navigation: true };
  }

  protected render() {
    if (this._configError) return this._message(this._configError);
    if (!this._config || !this._hass) return this._message(this._text("unavailable"));
    const entity = this._config.entity;
    if (!entity) return this._message(this._text("notFound"));
    const overview = this._hass.states[entity];
    if (!overview) return this._message(this._text("notFound"));
    const ids = discoverStationEntities(entity, overview, this._hass);
    const stations = ids.map((id) => ({ id, state: this._hass!.states[id]! })).filter(({ state }) => isUsableStation(state));
    const isUnavailable = unavailable.has(overview.state);
    const cooldown = this._cooldownState(overview);
    return html`
      <ha-card>
        <div class="header"><h2>${this._text("title")}</h2><span class="summary">${this._summary(overview, stations)}</span></div>
        ${this._controls(overview, cooldown)}
        ${this._providerStatus(overview)}
        ${this._controlError ? html`<div class="control-error" role="alert">${this._controlError}</div>` : nothing}
        ${isUnavailable ? html`<div class="message" role="status">${this._text("unavailable")}</div>` : nothing}
        ${!isUnavailable && this._hasRefreshError(overview) ? html`<div class="stale-warning" role="alert">${this._refreshError(overview, cooldown.display)}</div>` : nothing}
        ${!isUnavailable && this._fallbackMessage(overview) ? html`<div class="secondary" role="status">${this._fallbackMessage(overview)}</div>` : nothing}
        ${!isUnavailable && overview.attributes.data_stale === true ? html`<div class="stale-warning" role="status">${this._staleMessage(overview)}</div>` : nothing}
        ${!isUnavailable && overview.attributes.data_stale !== true && stations.some(({ state }) => state.attributes.price_stale === true) ? html`<div class="stale-warning" role="status">${this._text("providerPricesStale")}</div>` : nothing}
        ${this._hasNakordoni(overview, stations) ? html`<div class="secondary"><a href="https://nakordoni.eu" target="_blank" rel="noopener">Data by nakordoni.eu</a></div>` : nothing}
        ${!isUnavailable ? this._highlights(overview, ids) : nothing}
        ${!isUnavailable ? (stations.length ? html`<div class="stations">${stations.map(({ id, state }) => this._station(id, state))}</div>` : html`<div class="message">${this._text("none")}</div>`) : nothing}
      </ha-card>
    `;
  }

  private _controls(overview: HassState, cooldown: { backend: number; display: number }) {
    const entryId = text(overview.attributes.config_entry_id);
    if (!entryId || !this._hass?.callService || this._hass.user?.is_admin === false) return nothing;
    const mode = overview.attributes.fetch_mode === "manual" ? "manual" : "automatic";
    const busy = this._manualRefreshInFlight || this._modeChangeInFlight;
    const cooldownActive = cooldown.backend > 0;
    const backendAllowsRefresh = typeof overview.attributes.manual_refresh_available === "boolean"
      ? overview.attributes.manual_refresh_available
      : !cooldownActive;
    const blocked = !backendAllowsRefresh;
    return html`<div class="controls" aria-label="${this._text("fetchMode")}">
      <span class="control-label">${this._text("fetchMode")}</span>
      <div class="mode-switch" role="group" aria-label="${this._text("fetchMode")}">
        <button class=${mode === "automatic" ? "selected" : ""} ?disabled=${busy || mode === "automatic"} @click=${() => this._setFetchMode(entryId, "automatic")}>${this._text("automatic")}</button>
        <button class=${mode === "manual" ? "selected" : ""} ?disabled=${busy || mode === "manual"} @click=${() => this._setFetchMode(entryId, "manual")}>${this._text("manual")}</button>
      </div>
      ${mode === "manual" ? html`<button class="refresh" ?disabled=${busy || blocked} @click=${() => this._manualRefresh(entryId)}>${this._manualRefreshInFlight ? this._text("refreshing") : cooldownActive && blocked ? this._cooldownLabel(cooldown.display) : blocked ? this._text("noProviderAvailable") : this._text("refreshNow")}</button>` : nothing}
    </div>`;
  }

  private _providerStatus(overview: HassState) {
    const cooldowns = overview.attributes.provider_cooldowns && typeof overview.attributes.provider_cooldowns === "object"
      ? overview.attributes.provider_cooldowns as Record<string, Record<string, unknown>> : {};
    const quotas = overview.attributes.provider_quotas && typeof overview.attributes.provider_quotas === "object"
      ? overview.attributes.provider_quotas as Record<string, Record<string, unknown>> : {};
    const providers = Array.from(new Set([...Object.keys(cooldowns), ...Object.keys(quotas)]));
    if (!providers.length) return nothing;
    let activeCooldown = false;
    const rows = providers.map((provider) => {
      const cooldown = cooldowns[provider] ?? {};
      const quota = quotas[provider] ?? {};
      const cooldownSeconds = this._serverCooldownSeconds(cooldown);
      activeCooldown ||= cooldownSeconds > 0;
      const rawQuotas = quota.quotas && typeof quota.quotas === "object" ? quota.quotas as Record<string, Record<string, unknown>> : {};
      const cheap = rawQuotas.cheap;
      const remaining = cheap && Number.isInteger(cheap.remaining) ? Number(cheap.remaining) : undefined;
      const limit = cheap && Number.isInteger(cheap.limit) ? Number(cheap.limit) : undefined;
      const quotaText = quota.available === true && remaining !== undefined && limit !== undefined
        ? `${this._providerLabel(provider)} · ${remaining}/${limit} ${this._text("callsRemaining")}${quota.stale === true ? ` · ${this._text("quotaStale")}` : ""}`
        : `${this._providerLabel(provider)} · ${this._text("quotaUnavailable")}`;
      return html`<div class="secondary provider-status" role="status">
        ${cooldownSeconds > 0 ? html`${this._providerLabel(provider)} · ${this._text("cooldownActive")} · ${this._cooldownLabel(cooldownSeconds)}` : quotaText}
      </div>`;
    });
    if (!activeCooldown && Number(overview.attributes.provider_cooldown_remaining) <= 0 && this._cooldownTimer !== undefined) {
      window.clearInterval(this._cooldownTimer);
      this._cooldownTimer = undefined;
    }
    return html`<div class="provider-status-list" aria-label="${this._text("providerStatus")}">${rows}</div>`;
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

  private _summary(overview: HassState, stations: Array<{ id: string; state: HassState }>): string {
    const parts: string[] = [];
    const count = Number(overview.attributes.station_count);
    if (Number.isFinite(count)) parts.push(`${count} Tankstellen`);
    const radius = formatDistance(overview.attributes.radius, this._locale());
    if (radius) parts.push(radius);
    const fuels = Array.isArray(overview.attributes.fuel_types) ? overview.attributes.fuel_types : [overview.attributes.fuel_type];
    const labels = fuels.map((fuel) => fuelLabel(fuel)).filter((fuel): fuel is string => Boolean(fuel));
    if (labels.length) parts.push(labels.join(", "));
    if (overview.attributes.last_successful_update) {
      const date = new Date(String(overview.attributes.last_successful_update));
      if (!Number.isNaN(date.getTime())) parts.push(`${this._text("asOf")} ${new Intl.DateTimeFormat(this._locale(), { hour: "2-digit", minute: "2-digit" }).format(date)} (${this._relativeTime(date)})`);
    }
    parts.push(`${this._text("source")}: ${this._providerSummary(stations.map(({ state }) => state.attributes.provider))}`);
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
    const raw = Number(overview.attributes.provider_cooldown_remaining);
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

  private _cooldownLabel(seconds: number): string {
    const safe = Math.max(0, Math.ceil(seconds));
    return `${this._text("retryIn")} ${Math.floor(safe / 60)}:${String(safe % 60).padStart(2, "0")}`;
  }

  private _station(id: string, state: HassState) {
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
    const label = `${name}, ${priceRows.map((row) => `${row.fuel} ${row.value ?? this._text("noPrice")}`).join(", ")}`;
    const navigationUrl = this._config?.navigation !== false ? buildNavigationUrl(a.latitude, a.longitude, this._config?.navigation_provider ?? "auto") : null;
    return html`<div class="station" role="button" tabindex="0" aria-label="${label}" @click=${() => this._moreInfo(id)} @keydown=${(event: KeyboardEvent) => this._keyActivate(event, id)}>
      ${this._brandLogo(brand, name)}
      <div><div class="name">${name}${brand && shouldShowBrand(name, brand) ? html` <span class="secondary">(${brand})</span>` : nothing}</div>${address ? html`<div class="address">${address}</div>` : nothing}<div class="provider">${this._text("source")}: ${provider}</div>${status ? html`<div class=${open ? "open" : "closed"}>${open ? this._text("open") : this._text("closed")}</div>` : nothing}${freshness ? html`<div class="secondary">${freshness}</div>` : nothing}</div>
      <div class="prices">${priceRows.map((row) => html`<div class="fuel-price"><span>${row.fuel}${row.fallback ? html` <span class="secondary">(${this._text("fallback")})</span>` : nothing}</span><strong>${row.value ?? this._text("noPrice")}</strong></div>`)}${distance ? html`<div class="meta">${distance}</div>` : nothing}</div>
      ${navigationUrl ? html`<a class="navigate" href=${navigationUrl} target="_blank" rel="noopener noreferrer" aria-label="${this._text("navigate")}" @click=${(event: Event) => event.stopPropagation()}><ha-icon icon="mdi:navigation" aria-hidden="true"></ha-icon></a>` : nothing}
    </div>`;
  }

  private _message(message: string) { return html`<ha-card><div class="message">${message}</div></ha-card>`; }
  private _brandLogo(brand: unknown, alt: string) {
    const config = this._config;
    if (!config || config.show_brand_logos === false) return html`<ha-icon class="icon" icon="mdi:gas-station" aria-hidden="true"></ha-icon>`;
    const url = buildBrandLogoUrl(brand, config.logo_path, alt);
    const cacheKey = url ?? "fallback";
    if (!url || this._failedBrandLogos.has(cacheKey)) return html`<ha-icon class="icon" icon="mdi:gas-station" aria-label="${this._text("unknownBrand")}"></ha-icon>`;
    return html`<span class="brand-logo"><img src=${url} alt="${alt} ${this._text("brandLogo")}" @error=${() => { this._failedBrandLogos.add(cacheKey); this.requestUpdate(); }}></span>`;
  }
  private _locale(): string { return this._hass?.locale?.language?.toLowerCase().startsWith("en") ? "en-US" : "de-DE"; }
  private _text(key: "title" | "open" | "closed" | "noPrice" | "none" | "asOf" | "navigate" | "unavailable" | "notFound" | "selectEntity" | "nearest" | "cheapest" | "stale" | "lastSuccessful" | "priceAge" | "fallback" | "fallbackUsed" | "fallbackUnavailable" | "source" | "unknownSource" | "multipleSources" | "unknownBrand" | "brandLogo" | "fetchMode" | "automatic" | "manual" | "refreshNow" | "refreshing" | "refreshFailed" | "cooldownActive" | "retryIn" | "providerPricesStale" | "locationMissing" | "providerAuthFailed" | "providerRateLimited" | "providerQuotaExhausted" | "providerResponseError" | "networkTimeout" | "networkError" | "providerUnavailable" | "controlFailed" | "noProviderAvailable" | "providerStatus" | "callsRemaining" | "quotaStale" | "quotaUnavailable"): string {
    const english = this._locale() === "en-US";
    const values = english ? { title: "Nearby fuel stations", open: "Open", closed: "Closed", noPrice: "Price unavailable", none: "No fuel stations found", asOf: "As of", navigate: "Navigate", unavailable: "Fuel stations currently unavailable", notFound: "Overview entity not found", selectEntity: "Select an overview entity", nearest: "Nearest", cheapest: "Cheapest", stale: "Data stale", lastSuccessful: "last successful update", priceAge: "Confirmed", fallback: "E5 instead of E10", fallbackUsed: "Fallback provider used", fallbackUnavailable: "Fallback provider unavailable: market permission missing", source: "Source", unknownSource: "Source unknown", multipleSources: "Multiple data sources", unknownBrand: "Unknown station brand", brandLogo: "logo", fetchMode: "Fetch mode", automatic: "Automatic", manual: "Manual", refreshNow: "Fetch now", refreshing: "Fetching…", refreshFailed: "Station refresh failed", cooldownActive: "Provider cooldown active", retryIn: "Retry in", providerPricesStale: "Provider prices are stale", locationMissing: "Location data unavailable", providerAuthFailed: "Provider authentication failed", providerRateLimited: "Provider rate limit reached", providerQuotaExhausted: "Provider quota exhausted", providerResponseError: "Provider returned an invalid response", networkTimeout: "Provider request timed out", networkError: "Provider network error", providerUnavailable: "Provider temporarily unavailable", controlFailed: "Station control failed", noProviderAvailable: "No provider available", providerStatus: "Provider status", callsRemaining: "calls remaining", quotaStale: "quota data stale", quotaUnavailable: "quota unavailable" } : { title: "Tankstellen in der Nähe", open: "Geöffnet", closed: "Geschlossen", noPrice: "Preis nicht verfügbar", none: "Keine Tankstellen gefunden", asOf: "Stand", navigate: "Navigieren", unavailable: "Tankstellen derzeit nicht verfügbar", notFound: "Overview entity not found", selectEntity: "Bitte eine Overview-Entity auswählen", nearest: "Nächste", cheapest: "Günstigste", stale: "Daten veraltet", lastSuccessful: "letzte erfolgreiche Aktualisierung", priceAge: "Bestätigt", fallback: "E5 statt E10", fallbackUsed: "Ersatzanbieter verwendet", fallbackUnavailable: "Ersatzanbieter nicht verfügbar: Marktberechtigung fehlt", source: "Quelle", unknownSource: "Quelle unbekannt", multipleSources: "Mehrere Datenquellen", unknownBrand: "Unbekannte Tankstellenmarke", brandLogo: "Logo", fetchMode: "Abrufmodus", automatic: "Automatisch", manual: "Manuell", refreshNow: "Jetzt abrufen", refreshing: "Wird abgerufen…", refreshFailed: "Tankstellenabruf fehlgeschlagen", cooldownActive: "Provider-Cooldown aktiv", retryIn: "Erneut abrufen in", providerPricesStale: "Providerpreise sind veraltet", locationMissing: "Standortdaten fehlen", providerAuthFailed: "Provider-Authentifizierung fehlgeschlagen", providerRateLimited: "Provider-Limit erreicht", providerQuotaExhausted: "API-Kontingent erschöpft", providerResponseError: "Provider-Antwort konnte nicht verarbeitet werden", networkTimeout: "Netzwerk-/Timeout-Fehler beim Provider", networkError: "Netzwerkfehler beim Provider", providerUnavailable: "Provider ist vorübergehend nicht verfügbar", controlFailed: "Tankstellensteuerung fehlgeschlagen", noProviderAvailable: "Kein Provider verfügbar", providerStatus: "Providerstatus", callsRemaining: "Aufrufe verbleibend", quotaStale: "Kontingentdaten veraltet", quotaUnavailable: "Kontingent nicht verfügbar" };
    return values[key];
  }
  private _keyActivate(event: KeyboardEvent, id: string) { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); this._moreInfo(id); } }
  private _moreInfo(entityId: string) { this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId } })); }
}

class MobileFuelStationsCardEditor extends LitElement {
  static styles = css`
    :host { display: block; }
    label { display: block; color: var(--primary-text-color); margin: 8px 0; }
    select, input { box-sizing: border-box; width: 100%; padding: 8px; color: var(--primary-text-color); background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 4px; }
    .row { margin-top: 16px; }
  `;
  private _config: CardConfig = { navigation: true, navigation_provider: "auto", show_brand_logos: true, logo_path: DEFAULT_LOGO_PATH };
  private _hass?: Hass;
  setConfig(config: CardConfig): void { this._config = { ...config, navigation: config.navigation !== false, navigation_provider: config.navigation_provider ?? "auto", show_brand_logos: config.show_brand_logos !== false, logo_path: config.logo_path ?? DEFAULT_LOGO_PATH }; this.requestUpdate(); }
  set hass(value: Hass) { this._hass = value; this.requestUpdate(); }
  protected render() {
    const entities = Object.entries(this._hass?.states ?? {}).filter(([id, value]) => this._isOverview(id, value));
    return html`<label>${this._text("entity")}<select .value=${this._config.entity ?? ""} @change=${(event: Event) => this._changeEntity(event)}><option value="">${entities.length ? this._text("choose") : this._text("none")}</option>${entities.map(([id, value]) => html`<option value=${id}>${value?.attributes.friendly_name ?? id}</option>`)}</select></label><div class="row"><label><input type="checkbox" .checked=${this._config.navigation !== false} @change=${(event: Event) => this._changeNavigation(event)}> ${this._text("navigation")}</label></div><div class="row"><label>${this._text("provider")}<select .value=${this._config.navigation_provider ?? "auto"} .disabled=${this._config.navigation === false} @change=${(event: Event) => this._changeProvider(event)}><option value="auto">${this._text("auto")}</option><option value="apple">${this._text("apple")}</option><option value="google">${this._text("google")}</option><option value="waze">${this._text("waze")}</option></select></label></div><div class="row"><label><input type="checkbox" .checked=${this._config.show_brand_logos !== false} @change=${(event: Event) => this._changeBrandLogos(event)}> ${this._text("brandLogos")}</label><label>${this._text("logoPath")}<input .value=${this._config.logo_path ?? DEFAULT_LOGO_PATH} @change=${(event: Event) => this._changeLogoPath(event)}></label></div>`;
  }
  private _isOverview(id: string, value: HassState | undefined): boolean { return isOverviewEntity(id, value); }
  private _changeEntity(event: Event) { this._configChanged({ ...this._config, entity: (event.target as HTMLSelectElement).value }); }
  private _changeNavigation(event: Event) { this._configChanged({ ...this._config, navigation: (event.target as HTMLInputElement).checked }); }
  private _changeProvider(event: Event) { this._configChanged({ ...this._config, navigation_provider: (event.target as HTMLSelectElement).value as NavigationProvider }); }
  private _changeBrandLogos(event: Event) { this._configChanged({ ...this._config, show_brand_logos: (event.target as HTMLInputElement).checked }); }
  private _changeLogoPath(event: Event) { this._configChanged({ ...this._config, logo_path: (event.target as HTMLInputElement).value }); }
  private _configChanged(config: CardConfig) { this._config = config; this.dispatchEvent(new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config } })); }
  private _text(key: "entity" | "choose" | "none" | "navigation" | "provider" | "auto" | "apple" | "google" | "waze" | "selectEntity" | "brandLogos" | "logoPath"): string { return this._hass?.locale?.language?.toLowerCase().startsWith("en") ? { entity: "Overview entity", choose: "Select an entity", none: "No overview sensors found", navigation: "Show navigation", provider: "Navigation provider", auto: "Automatic", apple: "Apple Maps", google: "Google Maps", waze: "Waze", selectEntity: "Select an overview entity", brandLogos: "Show brand logos", logoPath: "Logo path" }[key] : { entity: "Overview-Entity", choose: "Bitte auswählen", none: "Keine Overview-Sensoren gefunden", navigation: "Navigation anzeigen", provider: "Navigationsanbieter", auto: "Automatisch", apple: "Apple Karten", google: "Google Maps", waze: "Waze", selectEntity: "Bitte eine Overview-Entity auswählen", brandLogos: "Markenlogos anzeigen", logoPath: "Logo-Pfad" }[key]; }
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
