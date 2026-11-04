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
    const int value_row = ui::line_height(Font::BODY_LARGE);
    const int gap = std::max(2, ui::mm(1));
    const int usable = std::max(1, context.width - padding * 2);
    const int available = std::max(1, context.height - padding * 2);
    const bool expanded = available >= row * 4 + value_row * 2 + gap * 2;
    const bool compact = available < row * 3 + value_row * 2 + gap;
    const bool single_line = available < value_row * 2 + gap;

    heading_ = ui::label(context.parent, Font::BODY, theme::INK_SOFT);
    nearest_title_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    nearest_ = ui::label(context.parent, Font::BODY_LARGE, theme::INK);
    cheapest_title_ = ui::label(context.parent, Font::BODY, theme::MUTED);
    cheapest_ = ui::label(context.parent, Font::BODY_LARGE, theme::INK);
    status_ = ui::label(context.parent, Font::BODY, theme::MUTED);

    for (auto *label : {heading_, nearest_title_, nearest_, cheapest_title_, cheapest_, status_}) {
      lv_obj_set_size(label, usable, row);
      lv_label_set_long_mode(label, LV_LABEL_LONG_CLIP);
    }

    int y = padding;
    lv_obj_set_height(nearest_, value_row);
    lv_obj_set_height(cheapest_, value_row);
    lv_obj_set_pos(heading_, padding, y);
    if (!compact) y += row + gap;
    lv_obj_set_pos(nearest_title_, padding, y);
    if (expanded) y += row;
    lv_obj_set_pos(nearest_, padding, y);
    y += value_row + gap;
    lv_obj_set_pos(cheapest_title_, padding, y);
    if (expanded) y += row;
    lv_obj_set_pos(cheapest_, padding, y);
    y += value_row;
    lv_obj_set_pos(status_, padding, y);
    if (compact) lv_obj_add_flag(heading_, LV_OBJ_FLAG_HIDDEN);
    if (single_line) lv_obj_add_flag(cheapest_, LV_OBJ_FLAG_HIDDEN);
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
    compact_ = compact;
    single_row_ = single_line;
    show_station_titles_(false);
  }

  void on_state(JsonObjectConst data) override {
    const char *state = data["state"] | "";
    JsonObjectConst attrs = data["attributes"].as<JsonObjectConst>();
    if (!attrs || !state[0] || std::string(state) == "unknown" ||
        std::string(state) == "unavailable") {
      nearest_line_ = plugin_->text("no_data");
      cheapest_line_.clear();
      show_cheapest_ = false;
      ui::set_text(nearest_, nearest_line_);
      ui::set_text(cheapest_, "");
      ui::set_text(status_, "");
      show_station_titles_(false);
      return;
    }

    const int count = attrs["station_count"] | 0;
    const bool stale = attrs["data_stale"] | false;
    show_station_titles_(count > 0);
    show_cheapest_ = false;
    if (count <= 0) {
      nearest_line_ = plugin_->text("unavailable");
      cheapest_line_.clear();
      show_cheapest_ = false;
      ui::set_text(nearest_, nearest_line_);
      ui::set_text(cheapest_, "");
    } else {
      nearest_line_ = station_line(expanded_ || compact_ ? "" : plugin_->text("nearest"), attrs,
                                         "nearest_name", "nearest_price",
                                         "nearest_distance", "nearest_currency");
      cheapest_line_ = station_line(expanded_ || compact_ ? "" : plugin_->text("cheapest"), attrs,
                                          "cheapest_name", "cheapest_price",
                                          "cheapest_distance", "cheapest_currency");
      ui::set_text(nearest_, single_row_ && show_cheapest_ ? cheapest_line_ : nearest_line_);
      ui::set_text(cheapest_, cheapest_line_);
    }
    ui::set_text(status_, stale ? plugin_->text("stale") : "");
  }

  // A tap cycles the highlighted station when only one row fits.
  // Tessera dispatches tile taps through on_tap(), not LVGL label callbacks.
  void on_tap() override {
    if (!single_row_ || cheapest_line_.empty()) return;
    show_cheapest_ = !show_cheapest_;
    ui::set_text(nearest_, show_cheapest_ ? cheapest_line_ : nearest_line_);
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
  void show_station_titles_(bool has_stations) {
    for (auto *title : {nearest_title_, cheapest_title_}) {
      if (expanded_ && has_stations) {
        lv_obj_remove_flag(title, LV_OBJ_FLAG_HIDDEN);
      } else {
        lv_obj_add_flag(title, LV_OBJ_FLAG_HIDDEN);
      }
    }
  }

  static std::string station_line(const std::string &label, JsonObjectConst data,
                                  const char *name_key, const char *price_key,
                                  const char *distance_key, const char *currency_key) {
    const char *name = data[name_key] | "--";
    const char *currency = data[currency_key] | "";
    const double distance = data[distance_key] | -1.0;
    const double price = data[price_key] | -1.0;
    char line[160];
    const char *prefix = label.empty() ? "" : ": ";
    if (std::isfinite(price) && price > 0 && std::isfinite(distance) && distance >= 0) {
      std::snprintf(line, sizeof(line), "%.3f %s / %.1f km - %.30s",
                    price, currency, distance, name);
    } else if (std::isfinite(price) && price > 0) {
      std::snprintf(line, sizeof(line), "%.3f %s - %.40s", price, currency, name);
    } else if (std::isfinite(distance) && distance >= 0) {
      std::snprintf(line, sizeof(line), "%.1f km - %.40s", distance, name);
    } else {
      std::snprintf(line, sizeof(line), "%s%s%.50s", label.c_str(), prefix, name);
    }
    return line;
  }

  const tessera::Plugin *plugin_;
  bool expanded_{false};
  bool compact_{false};
  bool single_row_{false};
  bool show_cheapest_{false};
  std::string nearest_line_;
  std::string cheapest_line_;
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
