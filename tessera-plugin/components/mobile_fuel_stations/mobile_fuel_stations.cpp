#include "mobile_fuel_stations.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace esphome::mobile_fuel_stations {
namespace ui = tessera::ui;
using tessera::Font;

namespace {
struct Station {
  std::string name, address, currency;
  double price{-1.0}, distance{-1.0}, age_hours{-1.0};
  bool open{false}, open_known{false}, stale{false};
};
struct Snapshot {
  bool valid{false}, stale{false};
  int count{0};
  std::vector<std::string> fuels;
  Station nearest, cheapest;
  std::vector<std::string> fuel_names;
  std::vector<Station> fuel_cheapest;
  std::vector<double> fuel_prices;
  std::string currency;
};

std::string string_value(JsonVariantConst value) {
  const char *text = value.as<const char *>();
  return text ? std::string(text) : std::string();
}

Station station_from(JsonObjectConst object) {
  Station station;
  station.name = string_value(object["station_name"]);
  if (station.name.empty()) station.name = string_value(object["name"]);
  station.currency = string_value(object["currency_symbol"]);
  if (station.currency.empty()) station.currency = string_value(object["currency"]);
  station.price = object["price"] | -1.0;
  station.distance = object["distance"] | -1.0;
  station.age_hours = object["price_age_hours"] | -1.0;
  if (station.age_hours < 0) station.age_hours = object["freshest_age_hours"] | -1.0;
  station.stale = object["station_stale"] | false;
  if (!station.stale) station.stale = object["price_stale"] | false;
  station.open_known = object["is_open"].is<bool>();
  station.open = object["is_open"] | false;
  const std::string street = string_value(object["street"]);
  const std::string number = string_value(object["house_number"]);
  const std::string postcode = string_value(object["postcode"]);
  const std::string place = string_value(object["place"]);
  station.address = street;
  if (!number.empty()) station.address += station.address.empty() ? number : " " + number;
  if (!postcode.empty() || !place.empty()) {
    if (!station.address.empty()) station.address += ", ";
    station.address += postcode;
    if (!postcode.empty() && !place.empty()) station.address += " ";
    station.address += place;
  }
  return station;
}

Snapshot snapshot_from(JsonObjectConst data) {
  Snapshot result;
  const char *state = data["state"] | "";
  if (!state[0] || std::string(state) == "unknown" || std::string(state) == "unavailable") return result;
  JsonObjectConst attrs = data["attributes"].as<JsonObjectConst>();
  if (!attrs) return result;
  result.valid = true;
  result.count = attrs["station_count"] | 0;
  result.stale = attrs["data_stale"] | false;
  if (attrs["fuel_types"].is<JsonArrayConst>()) {
    for (JsonVariantConst fuel : attrs["fuel_types"].as<JsonArrayConst>()) {
      const std::string value = string_value(fuel);
      if (!value.empty()) result.fuels.push_back(value);
    }
  }
  result.nearest = station_from(attrs["nearest_station"].as<JsonObjectConst>());
  result.cheapest = station_from(attrs["cheapest_station"].as<JsonObjectConst>());
  JsonObjectConst by_fuel = attrs["cheapest_stations_by_fuel"].as<JsonObjectConst>();
  if (by_fuel) {
    for (JsonPairConst pair : by_fuel) {
      const std::string fuel = pair.key().c_str();
      if (std::find(result.fuels.begin(), result.fuels.end(), fuel) == result.fuels.end()) result.fuels.push_back(fuel);
      result.fuel_names.push_back(fuel);
      result.fuel_cheapest.push_back(station_from(pair.value().as<JsonObjectConst>()));
    }
  }
  // Tessera sends explicit fields for entity tiles; nested object attributes are
  // used by the offline fixture but are not assumed to cross the wire.
  if (result.nearest.name.empty()) {
    result.nearest.name = string_value(attrs["nearest_name"]);
    result.nearest.price = attrs["nearest_price"] | -1.0;
    result.nearest.distance = attrs["nearest_distance"] | -1.0;
  }
  if (result.cheapest.name.empty()) {
    result.cheapest.name = string_value(attrs["cheapest_name"]);
    result.cheapest.price = attrs["cheapest_price"] | -1.0;
    result.cheapest.distance = attrs["cheapest_distance"] | -1.0;
  }
  result.currency = string_value(attrs["currency"]);
  if (result.nearest.currency.empty()) result.nearest.currency = result.currency;
  if (result.cheapest.currency.empty()) result.cheapest.currency = result.currency;
  if (attrs["cheapest_fuel_prices"].is<JsonArrayConst>()) {
    for (JsonVariantConst price : attrs["cheapest_fuel_prices"].as<JsonArrayConst>()) result.fuel_prices.push_back(price | -1.0);
  }
  return result;
}

std::string fit(std::string value, int width, Font font) {
  if (width <= 0 || ui::text_width(value, font) <= width) return value;
  while (value.size() > 1 && ui::text_width(value + "...", font) > width) value.pop_back();
  return value.empty() ? "..." : value + "...";
}
std::string price_text(const Station &station) {
  if (!std::isfinite(station.price) || station.price <= 0) return "--";
  char buffer[32];
  std::snprintf(buffer, sizeof(buffer), "%.3f %s", station.price, station.currency.c_str());
  return buffer;
}
std::string distance_text(const Station &station) {
  if (!std::isfinite(station.distance) || station.distance < 0) return "--";
  char buffer[24];
  std::snprintf(buffer, sizeof(buffer), "%.1f km", station.distance);
  return buffer;
}
std::string station_line(const Station &station) {
  return price_text(station) + " / " + distance_text(station) + " - " + (station.name.empty() ? "--" : station.name);
}
}  // namespace

class MobileFuelStationsCard;

class HighlightsTile : public tessera::Tile {
 public:
  explicit HighlightsTile(const MobileFuelStations *plugin) : plugin_(plugin) {}
  void create(const tessera::TileContext &context) override {
    const int pad = ui::mm(2), row = ui::line_height(Font::BODY), value = ui::line_height(Font::BODY_LARGE);
    const int gap = std::max(2, ui::mm(1)), width = std::max(1, context.width - pad * 2);
    const int height = std::max(1, context.height - pad * 2);
    expanded_ = height >= row * 4 + value * 2 + gap * 2;
    compact_ = height < row * 3 + value * 2 + gap;
    single_row_ = height < value * 2 + gap;
    entity_ = context.entity;
    tile_ = context.tile;
    heading_ = ui::label(context.parent, Font::BODY, theme::INK_SOFT);
    nearest_title_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    nearest_ = ui::label(context.parent, Font::BODY_LARGE, theme::INK);
    cheapest_title_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    cheapest_ = ui::label(context.parent, Font::BODY_LARGE, theme::INK);
    status_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    for (auto *label : {heading_, nearest_title_, nearest_, cheapest_title_, cheapest_, status_}) {
      lv_obj_set_width(label, width);
      lv_label_set_long_mode(label, LV_LABEL_LONG_DOT);
    }
    lv_obj_set_height(nearest_, value); lv_obj_set_height(cheapest_, value);
    int y = pad; lv_obj_set_pos(heading_, pad, y); if (!compact_) y += row + gap;
    lv_obj_set_pos(nearest_title_, pad, y); if (expanded_) y += row;
    lv_obj_set_pos(nearest_, pad, y); y += value + gap;
    lv_obj_set_pos(cheapest_title_, pad, y); if (expanded_) y += row;
    lv_obj_set_pos(cheapest_, pad, y); y += value; lv_obj_set_pos(status_, pad, y);
    if (compact_) lv_obj_add_flag(heading_, LV_OBJ_FLAG_HIDDEN);
    if (single_row_) lv_obj_add_flag(cheapest_, LV_OBJ_FLAG_HIDDEN);
    if (!expanded_) { lv_obj_add_flag(nearest_title_, LV_OBJ_FLAG_HIDDEN); lv_obj_add_flag(cheapest_title_, LV_OBJ_FLAG_HIDDEN); }
    if (y + row > context.height - pad) lv_obj_add_flag(status_, LV_OBJ_FLAG_HIDDEN);
    ui::set_text(heading_, plugin_->text("name")); ui::set_text(nearest_title_, plugin_->text("nearest"));
    ui::set_text(cheapest_title_, plugin_->text("cheapest")); ui::set_text(nearest_, plugin_->text("no_data"));
    ui::set_text(cheapest_, ""); ui::set_text(status_, "");
  }
  void on_state(JsonObjectConst data) override {
    snapshot_ = snapshot_from(data);
    if (!snapshot_.valid || snapshot_.count <= 0) {
      nearest_line_ = plugin_->text("no_data"); cheapest_line_.clear();
      ui::set_text(nearest_, nearest_line_); ui::set_text(cheapest_, "");
      ui::set_text(status_, snapshot_.valid ? plugin_->text("unavailable") : plugin_->text("no_data")); show_titles_(false); return;
    }
    if (!snapshot_.fuels.empty() && selected_fuel_ >= snapshot_.fuels.size()) selected_fuel_ = 0;
    nearest_line_ = station_line(snapshot_.nearest); cheapest_line_ = station_line(selected_station());
    ui::set_text(nearest_, fit(nearest_line_, lv_obj_get_width(nearest_), Font::BODY_LARGE));
    ui::set_text(cheapest_, fit(cheapest_line_, lv_obj_get_width(cheapest_), Font::BODY_LARGE));
    std::string status = snapshot_.stale ? plugin_->text("stale") : "";
    if (selected_fuel_ < snapshot_.fuels.size()) status = snapshot_.fuels[selected_fuel_] + (status.empty() ? "" : " - " + status);
    ui::set_text(status_, status); show_titles_(true);
  }
  void on_tap() override {
    tessera::open_card(plugin_->plugin_id(), "stations", entity_, tile_);
  }
  void on_theme() override {
    ui::set_color(heading_, theme::INK_SOFT); ui::set_color(nearest_title_, theme::MUTED); ui::set_color(nearest_, theme::INK);
    ui::set_color(cheapest_title_, theme::MUTED); ui::set_color(cheapest_, theme::INK); ui::set_color(status_, theme::MUTED);
  }
 private:
  Station selected_station() const {
    if (selected_fuel_ < snapshot_.fuels.size()) {
      for (size_t i = 0; i < snapshot_.fuel_names.size(); ++i)
        if (snapshot_.fuel_names[i] == snapshot_.fuels[selected_fuel_] && i < snapshot_.fuel_cheapest.size()) return snapshot_.fuel_cheapest[i];
    }
    Station station = snapshot_.cheapest;
    if (selected_fuel_ < snapshot_.fuel_prices.size() && snapshot_.fuel_prices[selected_fuel_] > 0)
      station.price = snapshot_.fuel_prices[selected_fuel_];
    return station;
  }
  void show_titles_(bool visible) { for (auto *label : {nearest_title_, cheapest_title_}) if (expanded_ && visible) lv_obj_remove_flag(label, LV_OBJ_FLAG_HIDDEN); else lv_obj_add_flag(label, LV_OBJ_FLAG_HIDDEN); }
  const MobileFuelStations *plugin_;
  Snapshot snapshot_; size_t selected_fuel_{0}; bool expanded_{false}, compact_{false}, single_row_{false};
  std::string nearest_line_, cheapest_line_, entity_; int tile_{-1};
  lv_obj_t *heading_{nullptr}, *nearest_title_{nullptr}, *nearest_{nullptr}, *cheapest_title_{nullptr}, *cheapest_{nullptr}, *status_{nullptr};
};

class MobileFuelStationsCard : public tessera::Card {
 public:
  explicit MobileFuelStationsCard(const MobileFuelStations *plugin) : plugin_(plugin) {}
  void open(const tessera::CardContext &context) override {
    parent_ = context.parent; width_ = context.width;
    title_ = ui::label(parent_, Font::TITLE, theme::INK); nearest_ = ui::label(parent_, Font::BODY_LARGE, theme::INK);
    cheapest_ = ui::label(parent_, Font::BODY_LARGE, theme::INK); address_ = ui::label(parent_, Font::BODY, theme::MUTED); status_ = ui::label(parent_, Font::BODY, theme::MUTED);
    for (auto *label : {title_, nearest_, cheapest_, address_, status_}) { lv_obj_set_width(label, std::max(1, width_ - ui::mm(8))); lv_label_set_long_mode(label, LV_LABEL_LONG_DOT); }
    int y = ui::mm(4); lv_obj_set_pos(title_, ui::mm(4), y); y += ui::line_height(Font::TITLE) + ui::mm(3);
    lv_obj_set_pos(nearest_, ui::mm(4), y); y += ui::line_height(Font::BODY_LARGE) + ui::mm(2);
    lv_obj_set_pos(cheapest_, ui::mm(4), y); y += ui::line_height(Font::BODY_LARGE) + ui::mm(2);
    lv_obj_set_pos(address_, ui::mm(4), y); y += ui::line_height(Font::BODY) + ui::mm(2); lv_obj_set_pos(status_, ui::mm(4), y);
    ui::set_text(title_, plugin_->text("details")); ui::set_text(nearest_, plugin_->text("no_data")); ui::set_text(cheapest_, ""); ui::set_text(address_, ""); ui::set_text(status_, plugin_->text("tap_to_switch"));
  }
  void on_state(JsonObjectConst data) override { snapshot_ = snapshot_from(data); render_(); }
  void on_tap() override {
    const tessera::Point point = tessera::tap_point();
    if (point.y >= 0 && point.y < ui::mm(20)) show_cheapest_ = !show_cheapest_;
    else if (!snapshot_.fuels.empty()) selected_fuel_ = (selected_fuel_ + 1) % snapshot_.fuels.size();
    render_();
  }
  void on_theme() override { ui::set_color(title_, theme::INK); ui::set_color(nearest_, theme::INK); ui::set_color(cheapest_, theme::INK); ui::set_color(address_, theme::MUTED); ui::set_color(status_, theme::MUTED); }
 private:
  Station selected_station() const {
    if (selected_fuel_ < snapshot_.fuels.size()) {
      for (size_t i = 0; i < snapshot_.fuel_names.size(); ++i)
        if (snapshot_.fuel_names[i] == snapshot_.fuels[selected_fuel_] && i < snapshot_.fuel_cheapest.size()) return snapshot_.fuel_cheapest[i];
    }
    Station station = snapshot_.cheapest;
    if (selected_fuel_ < snapshot_.fuel_prices.size() && snapshot_.fuel_prices[selected_fuel_] > 0)
      station.price = snapshot_.fuel_prices[selected_fuel_];
    return station;
  }
  void render_() {
    if (!snapshot_.valid || snapshot_.count <= 0) { ui::set_text(nearest_, plugin_->text("no_data")); ui::set_text(cheapest_, ""); ui::set_text(address_, ""); ui::set_text(status_, plugin_->text("unavailable")); return; }
    if (!snapshot_.fuels.empty() && selected_fuel_ >= snapshot_.fuels.size()) selected_fuel_ = 0;
    const Station &station = show_cheapest_ ? selected_station() : snapshot_.nearest;
    ui::set_text(nearest_, fit(station_line(station), lv_obj_get_width(nearest_), Font::BODY_LARGE));
    ui::set_text(cheapest_, fit(station.address.empty() ? plugin_->text("no_address") : station.address, lv_obj_get_width(cheapest_), Font::BODY_LARGE));
    ui::set_text(address_, station.open_known ? (station.open ? plugin_->text("open") : plugin_->text("closed")) : plugin_->text("status_unknown"));
    std::string status = snapshot_.fuels.empty() ? std::string() : std::string(plugin_->text("fuel")) + ": " + snapshot_.fuels[selected_fuel_];
    if (station.age_hours >= 0) { char age[48]; std::snprintf(age, sizeof(age), " - %.1f h", station.age_hours); status += age; }
    if (station.stale || snapshot_.stale) status += std::string(" - ") + plugin_->text("stale");
    ui::set_text(status_, fit(status, lv_obj_get_width(status_), Font::BODY));
  }
  const MobileFuelStations *plugin_; lv_obj_t *parent_{nullptr}, *title_{nullptr}, *nearest_{nullptr}, *cheapest_{nullptr}, *address_{nullptr}, *status_{nullptr};
  int width_{0}; size_t selected_fuel_{0}; bool show_cheapest_{false}; Snapshot snapshot_;
};

void MobileFuelStations::setup() { add_tile("highlights", [this]() { return new HighlightsTile(this); }); add_card("stations", [this]() { return new MobileFuelStationsCard(this); }); }

}  // namespace esphome::mobile_fuel_stations
