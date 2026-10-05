import { LitElement, css, html, nothing } from "lit";

type HassState = {
  state: string;
  attributes: Record<string, unknown>;
};

type Hass = {
  states: Record<string, HassState | undefined>;
  localize?: (key: string, ...args: unknown[]) => string;
};

type CardConfig = { type: string; entity: string };

const unavailable = new Set(["unknown", "unavailable"]);

export function formatPrice(value: unknown, locale = "de-DE"): string | null {
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(number)) return null;
  return `${new Intl.NumberFormat(locale, { minimumFractionDigits: 3, maximumFractionDigits: 3 }).format(number)} €/l`;
}

export function formatDistance(value: unknown, locale = "de-DE"): string | null {
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(number)) return null;
  return `${new Intl.NumberFormat(locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(number)} km`;
}

export function fuelLabel(value: unknown): string | null {
  const labels: Record<string, string> = { diesel: "Diesel", e5: "E5", e10: "E10" };
  return typeof value === "string" ? labels[value.toLowerCase()] ?? value : null;
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

function text(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

export class MobileFuelStationsCard extends LitElement {
  static styles = css`
    :host { display: block; }
    ha-card { padding: 16px; color: var(--primary-text-color); background: var(--card-background-color); border-radius: var(--ha-card-border-radius, 12px); }
    .header { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; margin-bottom: 12px; }
    h2 { margin: 0; font-size: 1.1rem; }
    .summary, .secondary { color: var(--secondary-text-color); font-size: .9rem; }
    .stations { display: grid; gap: 8px; }
    .station { display: grid; grid-template-columns: 32px minmax(0, 1fr) auto; gap: 10px; align-items: center; border-top: 1px solid var(--divider-color); padding: 12px 0; cursor: pointer; }
    .station:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
    .icon { color: var(--primary-color); font-size: 1.5rem; }
    .name, .address { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .name { font-weight: 500; }
    .address { color: var(--secondary-text-color); font-size: .85rem; }
    .price { font-size: 1.05rem; font-weight: 700; text-align: right; white-space: nowrap; }
    .meta { color: var(--secondary-text-color); font-size: .82rem; text-align: right; white-space: nowrap; }
    .open { color: var(--success-color, var(--primary-color)); }
    .closed { color: var(--secondary-text-color); }
    .message { color: var(--secondary-text-color); }
    @media (min-width: 700px) { .stations { grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 18px; } .station { min-width: 0; } }
  `;

  private _config?: CardConfig;
  private _hass?: Hass;
  private _configError?: string;

  setConfig(config: Partial<CardConfig>): void {
    if (!config || typeof config.entity !== "string" || !config.entity.trim()) {
      throw new Error("Mobile Fuel Stations Card benötigt eine entity-Konfiguration.");
    }
    this._config = { type: config.type ?? "custom:mobile-fuel-stations-card", entity: config.entity };
    this._configError = undefined;
    this.requestUpdate();
  }

  set hass(value: Hass) { this._hass = value; this.requestUpdate(); }
  get hass(): Hass | undefined { return this._hass; }

  static getStubConfig(): CardConfig { return { type: "custom:mobile-fuel-stations-card", entity: "sensor.example_nearby_stations" }; }

  protected render() {
    if (this._configError) return this._message(this._configError);
    if (!this._config || !this._hass) return this._message("Tankstellen derzeit nicht verfügbar");
    const overview = this._hass.states[this._config.entity];
    if (!overview) return this._message("Overview entity not found");
    if (unavailable.has(overview.state)) return this._message("Tankstellen derzeit nicht verfügbar");

    const ids = discoverStationEntities(this._config.entity, overview, this._hass);
    const stations = ids.map((id) => ({ id, state: this._hass!.states[id]! })).filter(({ state }) => isUsableStation(state));
    return html`
      <ha-card>
        <div class="header"><h2>Tankstellen in der Nähe</h2><span class="summary">${this._summary(overview)}</span></div>
        ${stations.length ? html`<div class="stations">${stations.map(({ id, state }) => this._station(id, state))}</div>` : html`<div class="message">Keine Tankstellen gefunden</div>`}
      </ha-card>
    `;
  }

  private _summary(overview: HassState): string {
    const parts: string[] = [];
    const count = Number(overview.attributes.station_count);
    if (Number.isFinite(count)) parts.push(`${count} Tankstellen`);
    const radius = formatDistance(overview.attributes.radius);
    if (radius) parts.push(radius);
    const fuel = fuelLabel(overview.attributes.fuel_type);
    if (fuel) parts.push(fuel);
    if (overview.attributes.last_successful_update) {
      const date = new Date(String(overview.attributes.last_successful_update));
      if (!Number.isNaN(date.getTime())) parts.push(`Stand ${new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(date)}`);
    }
    return parts.join(" · ");
  }

  private _station(id: string, state: HassState) {
    const a = state.attributes;
    const name = text(a.station_name) ?? text(a.name) ?? id;
    const brand = text(a.brand);
    const addressParts = [a.street && a.house_number ? `${a.street} ${a.house_number}` : text(a.street), [a.postcode, a.place].filter(Boolean).join(" ")].filter(Boolean);
    const address = addressParts.join(", ");
    const price = formatPrice(state.state);
    const distance = formatDistance(a.distance);
    const open = typeof a.is_open === "boolean" ? a.is_open : undefined;
    const status = open === undefined ? null : open ? "Geöffnet" : "Geschlossen";
    const label = `${name}${price ? `, ${price}` : ""}`;
    return html`<div class="station" role="button" tabindex="0" aria-label="${label}" @click=${() => this._moreInfo(id)} @keydown=${(event: KeyboardEvent) => this._keyActivate(event, id)}>
      <ha-icon class="icon" icon="mdi:gas-station" aria-hidden="true"></ha-icon>
      <div><div class="name">${name}${brand ? html` <span class="secondary">(${brand})</span>` : nothing}</div>${address ? html`<div class="address">${address}</div>` : nothing}${status ? html`<div class=${open ? "open" : "closed"}>${status}</div>` : nothing}</div>
      <div><div class="price">${price ?? "Preis nicht verfügbar"}</div>${distance ? html`<div class="meta">${distance}</div>` : nothing}</div>
    </div>`;
  }

  private _message(message: string) { return html`<ha-card><div class="message">${message}</div></ha-card>`; }
  private _keyActivate(event: KeyboardEvent, id: string) { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); this._moreInfo(id); } }
  private _moreInfo(entityId: string) { this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId } })); }
}

customElements.define("mobile-fuel-stations-card", MobileFuelStationsCard);

declare global { interface Window { customCards?: Array<Record<string, string>>; } }
window.customCards = window.customCards ?? [];
if (!window.customCards.some((card) => card.type === "mobile-fuel-stations-card")) {
  window.customCards.push({ type: "mobile-fuel-stations-card", name: "Mobile Fuel Stations", description: "Nearby fuel stations from the Mobile Fuel Stations integration" });
}
