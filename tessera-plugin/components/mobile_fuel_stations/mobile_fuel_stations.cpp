#include "mobile_fuel_stations.h"

#include <cmath>
#include <cstdio>
#include <string>

namespace esphome::mobile_fuel_stations {

namespace ui = tessera::ui;
using tessera::Font;

// Read-only highlights. No network access, credentials, or Home Assistant
// actions. All data is received from the selected overview sensor.
class HighlightsTile : public tessera::Tile {
 public:
  explicit HighlightsTile(const tessera::Plugin *plugin) : plugin_(plugin) {}

  void create(const tessera::TileContext &context) override {
    width_ = context.width;
    const int padding = ui::mm(2);
    const int row_height = ui::line_height(Font::BODY);
    heading_ = ui::label(context.parent, Font::BODY, theme::INK_SOFT);
    nearest_ = ui::label(context.parent, Font::BODY, theme::INK);
    cheapest_ = ui::label(context.parent, Font::BODY, theme::INK);
    status_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    for (auto *label : {heading_, nearest_, cheapest_, status_}) {
      lv_obj_set_width(label, width_ - padding * 2);
    }
    lv_obj_set_pos(heading_, padding, padding);
    lv_obj_set_pos(nearest_, padding, padding + row_height);
    lv_obj_set_pos(cheapest_, padding, padding + row_height * 2);
    lv_obj_set_pos(status_, padding, padding + row_height * 3);
    ui::set_text(heading_, "Mobile Fuel Stations");
    ui::set_text(nearest_, plugin_->text("no_data"));
    ui::set_text(cheapest_, "");
    ui::set_text(status_, "");
  }

  void on_state(JsonObjectConst data) override {
    const char *state = data["state"] | "";
    JsonObjectConst attrs = data["attributes"].as<JsonObjectConst>();
    if (!attrs || !state[0] || std::string(state) == "unknown" ||
        std::string(state) == "unavailable") {
      ui::set_text(nearest_, plugin_->text("no_data"));
      ui::set_text(cheapest_, "");
      ui::set_text(status_, "");
      return;
    }

    const int count = attrs["station_count"] | 0;
    const bool stale = attrs["data_stale"] | false;
    if (count <= 0) {
      ui::set_text(nearest_, plugin_->text("unavailable"));
      ui::set_text(cheapest_, "");
    } else {
      ui::set_text(nearest_, station_line(plugin_->text("nearest"), data,
                                         "nearest_name", "nearest_price",
                                         "nearest_distance", "nearest_currency"));
      ui::set_text(cheapest_, station_line(plugin_->text("cheapest"), data,
                                          "cheapest_name", "cheapest_price",
                                          "cheapest_distance", "cheapest_currency"));
    }
    ui::set_text(status_, stale ? plugin_->text("stale") : "");
  }

  void on_theme() override {
    ui::set_color(heading_, theme::INK_SOFT);
    ui::set_color(nearest_, theme::INK);
    ui::set_color(cheapest_, theme::INK);
    ui::set_color(status_, theme::MUTED);
  }

 private:
  static std::string station_line(const char *label, JsonObjectConst data,
                                  const char *name_key, const char *price_key,
                                  const char *distance_key, const char *currency_key) {
    const char *name = data[name_key] | "--";
    const char *currency = data[currency_key] | "";
    const double distance = data[distance_key] | -1.0;
    const double price = data[price_key] | -1.0;
    char line[160];
    if (std::isfinite(price) && price > 0 && std::isfinite(distance) && distance >= 0) {
      std::snprintf(line, sizeof(line), "%s: %.30s %.3f %s / %.1f km",
                    label, name, price, currency, distance);
    } else if (std::isfinite(distance) && distance >= 0) {
      std::snprintf(line, sizeof(line), "%s: %.40s / %.1f km", label, name, distance);
    } else {
      std::snprintf(line, sizeof(line), "%s: %.50s", label, name);
    }
    return line;
  }

  const tessera::Plugin *plugin_;
  int width_{0};
  lv_obj_t *heading_{nullptr};
  lv_obj_t *nearest_{nullptr};
  lv_obj_t *cheapest_{nullptr};
  lv_obj_t *status_{nullptr};
};

void MobileFuelStations::setup() {
  add_tile("highlights", [this]() { return new HighlightsTile(this); });
}

}  // namespace esphome::mobile_fuel_stations
