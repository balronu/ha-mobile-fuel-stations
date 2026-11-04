#include "mobile_fuel_stations.h"

#include <algorithm>
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
    const int padding = ui::mm(2);
    const int row = ui::line_height(Font::BODY);
    const int gap = std::max(2, ui::mm(1));
    const int usable = std::max(1, context.width - padding * 2);
    const int available = std::max(1, context.height - padding * 2);
    const bool expanded = available >= row * 6 + gap * 2;

    heading_ = ui::label(context.parent, Font::BODY, theme::INK_SOFT);
    nearest_title_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    nearest_ = ui::label(context.parent, Font::BODY, theme::INK);
    cheapest_title_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    cheapest_ = ui::label(context.parent, Font::BODY, theme::INK);
    status_ = ui::label(context.parent, Font::BODY, theme::MUTED);

    for (auto *label : {heading_, nearest_title_, nearest_, cheapest_title_, cheapest_, status_}) {
      lv_obj_set_size(label, usable, row);
      lv_label_set_long_mode(label, LV_LABEL_LONG_CLIP);
    }

    int y = padding;
    lv_obj_set_pos(heading_, padding, y);
    y += row + gap;
    lv_obj_set_pos(nearest_title_, padding, y);
    if (expanded) y += row;
    lv_obj_set_pos(nearest_, padding, y);
    y += row + gap;
    lv_obj_set_pos(cheapest_title_, padding, y);
    if (expanded) y += row;
    lv_obj_set_pos(cheapest_, padding, y);
    y += row;
    lv_obj_set_pos(status_, padding, y);
    if (!expanded) {
      lv_obj_add_flag(nearest_title_, LV_OBJ_FLAG_HIDDEN);
      lv_obj_add_flag(cheapest_title_, LV_OBJ_FLAG_HIDDEN);
    }
    if (y + row > context.height - padding) lv_obj_add_flag(status_, LV_OBJ_FLAG_HIDDEN);
    ui::set_text(heading_, "Mobile Fuel Stations");
    ui::set_text(nearest_title_, plugin_->text("nearest"));
    ui::set_text(cheapest_title_, plugin_->text("cheapest"));
    ui::set_text(nearest_, plugin_->text("no_data"));
    ui::set_text(cheapest_, "");
    ui::set_text(status_, "");
    expanded_ = expanded;
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
      ui::set_text(nearest_, station_line(expanded_ ? "" : plugin_->text("nearest"), attrs,
                                         "nearest_name", "nearest_price",
                                         "nearest_distance", "nearest_currency"));
      ui::set_text(cheapest_, station_line(expanded_ ? "" : plugin_->text("cheapest"), attrs,
                                          "cheapest_name", "cheapest_price",
                                          "cheapest_distance", "cheapest_currency"));
    }
    ui::set_text(status_, stale ? plugin_->text("stale") : "");
  }

  void on_theme() override {
    ui::set_color(heading_, theme::INK_SOFT);
    ui::set_color(nearest_title_, theme::MUTED);
    ui::set_color(nearest_, theme::INK);
    ui::set_color(cheapest_title_, theme::MUTED);
    ui::set_color(cheapest_, theme::INK);
    ui::set_color(status_, theme::MUTED);
  }

 private:
  static std::string station_line(const std::string &label, JsonObjectConst data,
                                  const char *name_key, const char *price_key,
                                  const char *distance_key, const char *currency_key) {
    const char *name = data[name_key] | "--";
    const char *currency = data[currency_key] | "";
    const double distance = data[distance_key] | -1.0;
    const double price = data[price_key] | -1.0;
    char line[160];
    if (std::isfinite(price) && price > 0 && std::isfinite(distance) && distance >= 0) {
      std::snprintf(line, sizeof(line), "%s: %.30s %.3f %s / %.1f km",
                    label.c_str(), name, price, currency, distance);
    } else if (std::isfinite(distance) && distance >= 0) {
      std::snprintf(line, sizeof(line), "%s: %.40s / %.1f km", label.c_str(), name, distance);
    } else {
      std::snprintf(line, sizeof(line), "%s: %.50s", label.c_str(), name);
    }
    return line;
  }

  const tessera::Plugin *plugin_;
  bool expanded_{false};
  lv_obj_t *heading_{nullptr};
  lv_obj_t *nearest_title_{nullptr};
  lv_obj_t *nearest_{nullptr};
  lv_obj_t *cheapest_title_{nullptr};
  lv_obj_t *cheapest_{nullptr};
  lv_obj_t *status_{nullptr};
};

void MobileFuelStations::setup() {
  add_tile("highlights", [this]() { return new HighlightsTile(this); });
}

}  // namespace esphome::mobile_fuel_stations
