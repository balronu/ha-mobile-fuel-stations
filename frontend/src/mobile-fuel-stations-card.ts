import { LitElement, css, html, nothing } from "lit";

type HassState = {
  state: string;
  attributes: Record<string, unknown>;
};

type Hass = {
  states: Record<string, HassState | undefined>;
  locale?: { language?: string };
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
  fuel_prices?: Record<string, number | null>;
  fuel_fallbacks?: Record<string, boolean>;
};

export type NavigationProvider = "auto" | "apple" | "google" | "waze";
type CardConfig = { type?: string; entity?: string; navigation?: boolean; navigation_provider?: NavigationProvider };

const unavailable = new Set(["unknown", "unavailable"]);

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

function isOverviewEntity(entityId: string, state: HassState | undefined): boolean {
  if (!entityId.startsWith("sensor.") || !state) return false;
  if (Array.isArray(state.attributes.station_entities)) return true;
  const mobileFuelMarkers = ["location_entity", "radius", "fuel_type", "station_count"]
    .filter((key) => state.attributes[key] !== undefined).length;
  return entityId.endsWith("_nearby_stations") && mobileFuelMarkers >= 2;
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
    :host { display: block; }
    ha-card { padding: 16px; color: var(--primary-text-color); background: var(--card-background-color); border-radius: var(--ha-card-border-radius, 12px); }
    .header { display: block; margin-bottom: 12px; }
    h2 { margin: 0; font-size: 1.1rem; }
    .summary, .secondary { color: var(--secondary-text-color); font-size: .9rem; }
    .summary { display: block; margin-top: 4px; }
    .stations { display: grid; gap: 4px; }
    .station { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto auto; gap: 8px; align-items: center; border-top: 1px solid var(--divider-color); padding: 8px 0; cursor: pointer; min-width: 0; }
    .station:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .icon { color: var(--primary-color); font-size: 1.5rem; }
    .name, .address { overflow-wrap: anywhere; word-break: break-word; }
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
    .highlights { display: grid; gap: 6px; margin-bottom: 10px; }
    .highlight { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; gap: 8px; align-items: center; border: 1px solid var(--divider-color); border-radius: var(--ha-card-border-radius, 12px); padding: 8px 10px; min-width: 0; }
    .highlight.is-link { cursor: pointer; }
    .highlight.is-link:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .highlight-label { color: var(--secondary-text-color); font-size: .82rem; font-weight: 600; text-transform: uppercase; }
    .highlight-name { font-weight: 600; margin-top: 3px; overflow-wrap: anywhere; word-break: break-word; }
    .highlight-meta { color: var(--secondary-text-color); font-size: .9rem; margin-top: 3px; }
    @media (min-width: 700px) { .highlights { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (min-width: 700px) { .header { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; } .summary { margin-top: 0; } .stations { grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 18px; } .station { min-width: 0; } }
    @media (max-width: 480px) { ha-card { padding: 12px; } .station { grid-template-columns: 26px minmax(0, 1fr) auto; gap: 6px; } .station .prices { grid-column: 2; grid-row: 2; text-align: left; } .fuel-price { justify-content: flex-start; gap: 4px; } .station .navigate { grid-column: 3; grid-row: 1 / span 2; align-self: center; } .highlight { grid-template-columns: minmax(0, 1fr) auto auto; gap: 6px; } .highlight .navigate { grid-column: auto; } }
  `;

  private _config?: CardConfig;
  private _hass?: Hass;
  private _configError?: string;

  setConfig(config: Partial<CardConfig>): void {
    if (!config || typeof config.entity !== "string" || !config.entity.trim()) {
      this._config = { ...(config ?? {}), type: config?.type ?? "custom:mobile-fuel-stations-card", navigation: config?.navigation !== false, navigation_provider: config?.navigation_provider ?? "auto" };
      this._configError = this._text("selectEntity");
      this.requestUpdate();
      return;
    }
    this._config = { ...config, type: config.type ?? "custom:mobile-fuel-stations-card", entity: config.entity, navigation: config.navigation !== false, navigation_provider: config.navigation_provider ?? "auto" };
    this._configError = undefined;
    this.requestUpdate();
  }

  set hass(value: Hass) { this._hass = value; this.requestUpdate(); }
  get hass(): Hass | undefined { return this._hass; }

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
    if (unavailable.has(overview.state)) return this._message(this._text("unavailable"));

    const ids = discoverStationEntities(entity, overview, this._hass);
    const stations = ids.map((id) => ({ id, state: this._hass!.states[id]! })).filter(({ state }) => isUsableStation(state));
    return html`
      <ha-card>
        <div class="header"><h2>${this._text("title")}</h2><span class="summary">${this._summary(overview)}</span></div>
        ${overview.attributes.provider === "nakordoni" ? html`<div class="secondary"><a href="https://nakordoni.eu" target="_blank" rel="noopener">Data by nakordoni.eu</a></div>` : nothing}
        ${this._highlights(overview, ids)}
        ${stations.length ? html`<div class="stations">${stations.map(({ id, state }) => this._station(id, state))}</div>` : html`<div class="message">${this._text("none")}</div>`}
      </ha-card>
    `;
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
    const navigationUrl = this._config?.navigation !== false ? buildNavigationUrl(station.latitude, station.longitude, this._config?.navigation_provider ?? "auto") : null;
    const address = [station.street && station.house_number ? `${station.street} ${station.house_number}` : text(station.street), [station.postcode, station.place].filter(Boolean).join(" ")].filter(Boolean).join(", ");
    return html`<div class="highlight${entityId ? " is-link" : ""}" role=${entityId ? "button" : nothing} tabindex=${entityId ? "0" : nothing} aria-label="${name}" @click=${entityId ? () => this._moreInfo(entityId) : undefined} @keydown=${entityId ? (event: KeyboardEvent) => this._keyActivate(event, entityId) : undefined}>
      <div><div class="highlight-label">${label}</div><div class="highlight-name">${name}${brand && shouldShowBrand(name, brand) ? html` <span class="secondary">(${brand})</span>` : nothing}</div>${address ? html`<div class="address">${address}</div>` : nothing}</div>
      <div><div class="price">${price}</div>${distance ? html`<div class="meta">${distance}</div>` : nothing}</div>
      ${navigationUrl ? html`<a class="navigate" href=${navigationUrl} target="_blank" rel="noopener noreferrer" aria-label="${this._text("navigate")}" @click=${(event: Event) => event.stopPropagation()}><ha-icon icon="mdi:navigation" aria-hidden="true"></ha-icon></a>` : nothing}
    </div>`;
  }

  private _summary(overview: HassState): string {
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
      if (!Number.isNaN(date.getTime())) parts.push(`${this._text("asOf")} ${new Intl.DateTimeFormat(this._locale(), { hour: "2-digit", minute: "2-digit" }).format(date)}`);
    }
    return parts.join(" · ");
  }

  private _station(id: string, state: HassState) {
    const a = state.attributes;
    const name = text(a.station_name) ?? text(a.name) ?? id;
    const brand = text(a.brand);
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
      <ha-icon class="icon" icon="mdi:gas-station" aria-hidden="true"></ha-icon>
      <div><div class="name">${name}${brand && shouldShowBrand(name, brand) ? html` <span class="secondary">(${brand})</span>` : nothing}</div>${address ? html`<div class="address">${address}</div>` : nothing}${status ? html`<div class=${open ? "open" : "closed"}>${open ? this._text("open") : this._text("closed")}</div>` : nothing}${freshness ? html`<div class="secondary">${freshness}</div>` : nothing}</div>
      <div class="prices">${priceRows.map((row) => html`<div class="fuel-price"><span>${row.fuel}${row.fallback ? html` <span class="secondary">(${this._text("fallback")})</span>` : nothing}</span><strong>${row.value ?? this._text("noPrice")}</strong></div>`)}${distance ? html`<div class="meta">${distance}</div>` : nothing}</div>
      ${navigationUrl ? html`<a class="navigate" href=${navigationUrl} target="_blank" rel="noopener noreferrer" aria-label="${this._text("navigate")}" @click=${(event: Event) => event.stopPropagation()}><ha-icon icon="mdi:navigation" aria-hidden="true"></ha-icon></a>` : nothing}
    </div>`;
  }

  private _message(message: string) { return html`<ha-card><div class="message">${message}</div></ha-card>`; }
  private _locale(): string { return this._hass?.locale?.language?.toLowerCase().startsWith("en") ? "en-US" : "de-DE"; }
  private _text(key: "title" | "open" | "closed" | "noPrice" | "none" | "asOf" | "navigate" | "unavailable" | "notFound" | "selectEntity" | "nearest" | "cheapest" | "stale" | "priceAge" | "fallback"): string {
    const english = this._locale() === "en-US";
    const values = english ? { title: "Nearby fuel stations", open: "Open", closed: "Closed", noPrice: "Price unavailable", none: "No fuel stations found", asOf: "As of", navigate: "Navigate to station", unavailable: "Fuel stations currently unavailable", notFound: "Overview entity not found", selectEntity: "Select an overview entity", nearest: "Nearest", cheapest: "Cheapest", stale: "Price stale", priceAge: "Confirmed", fallback: "E5 instead of E10" } : { title: "Tankstellen in der Nähe", open: "Geöffnet", closed: "Geschlossen", noPrice: "Preis nicht verfügbar", none: "Keine Tankstellen gefunden", asOf: "Stand", navigate: "Navigieren", unavailable: "Tankstellen derzeit nicht verfügbar", notFound: "Overview entity not found", selectEntity: "Bitte eine Overview-Entity auswählen", nearest: "Nächste", cheapest: "Günstigste", stale: "Preis veraltet", priceAge: "Bestätigt", fallback: "E5 statt E10" };
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
  private _config: CardConfig = { navigation: true, navigation_provider: "auto" };
  private _hass?: Hass;
  setConfig(config: CardConfig): void { this._config = { ...config, navigation: config.navigation !== false, navigation_provider: config.navigation_provider ?? "auto" }; this.requestUpdate(); }
  set hass(value: Hass) { this._hass = value; this.requestUpdate(); }
  protected render() {
    const entities = Object.entries(this._hass?.states ?? {}).filter(([id, value]) => this._isOverview(id, value));
    return html`<label>${this._text("entity")}<select .value=${this._config.entity ?? ""} @change=${(event: Event) => this._changeEntity(event)}><option value="">${entities.length ? this._text("choose") : this._text("none")}</option>${entities.map(([id, value]) => html`<option value=${id}>${value?.attributes.friendly_name ?? id}</option>`)}</select></label><div class="row"><label><input type="checkbox" .checked=${this._config.navigation !== false} @change=${(event: Event) => this._changeNavigation(event)}> ${this._text("navigation")}</label></div><div class="row"><label>${this._text("provider")}<select .value=${this._config.navigation_provider ?? "auto"} .disabled=${this._config.navigation === false} @change=${(event: Event) => this._changeProvider(event)}><option value="auto">${this._text("auto")}</option><option value="apple">${this._text("apple")}</option><option value="google">${this._text("google")}</option><option value="waze">${this._text("waze")}</option></select></label></div>`;
  }
  private _isOverview(id: string, value: HassState | undefined): boolean { return Boolean(id.startsWith("sensor.") && value && (Array.isArray(value.attributes.station_entities) || (id.endsWith("_nearby_stations") && value.attributes.station_count !== undefined))); }
  private _changeEntity(event: Event) { this._configChanged({ ...this._config, entity: (event.target as HTMLSelectElement).value }); }
  private _changeNavigation(event: Event) { this._configChanged({ ...this._config, navigation: (event.target as HTMLInputElement).checked }); }
  private _changeProvider(event: Event) { this._configChanged({ ...this._config, navigation_provider: (event.target as HTMLSelectElement).value as NavigationProvider }); }
  private _configChanged(config: CardConfig) { this._config = config; this.dispatchEvent(new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config } })); }
  private _text(key: "entity" | "choose" | "none" | "navigation" | "provider" | "auto" | "apple" | "google" | "waze" | "selectEntity"): string { return this._hass?.locale?.language?.toLowerCase().startsWith("en") ? { entity: "Overview entity", choose: "Select an entity", none: "No overview sensors found", navigation: "Show navigation", provider: "Navigation provider", auto: "Automatic", apple: "Apple Maps", google: "Google Maps", waze: "Waze", selectEntity: "Select an overview entity" }[key] : { entity: "Overview-Entity", choose: "Bitte auswählen", none: "Keine Overview-Sensoren gefunden", navigation: "Navigation anzeigen", provider: "Navigationsanbieter", auto: "Automatisch", apple: "Apple Karten", google: "Google Maps", waze: "Waze", selectEntity: "Bitte eine Overview-Entity auswählen" }[key]; }
}

if (!customElements.get("mobile-fuel-stations-card")) {
  customElements.define("mobile-fuel-stations-card", MobileFuelStationsCard);
}
if (!customElements.get("mobile-fuel-stations-card-editor")) {
  customElements.define("mobile-fuel-stations-card-editor", MobileFuelStationsCardEditor);
}

declare global { interface Window { customCards?: Array<Record<string, unknown>>; } }
window.customCards = window.customCards ?? [];
if (!window.customCards.some((card) => card.type === "mobile-fuel-stations-card")) {
  window.customCards.push({ type: "mobile-fuel-stations-card", name: "Mobile Fuel Stations", description: "Nearby fuel stations from the Mobile Fuel Stations integration", getEntitySuggestion: (hass: Hass, entityId: string) => isOverviewEntity(entityId, hass.states[entityId]) ? { config: { type: "custom:mobile-fuel-stations-card", entity: entityId } } : null });
}
