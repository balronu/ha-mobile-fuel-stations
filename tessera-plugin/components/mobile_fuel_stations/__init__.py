"""ESPHome code generation for the Tessera Mobile Fuel Stations plugin."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import smart_display
from esphome.const import CONF_ID

DEPENDENCIES = ["smart_display"]

mobile_fuel_stations_ns = cg.esphome_ns.namespace("mobile_fuel_stations")
MobileFuelStations = mobile_fuel_stations_ns.class_("MobileFuelStations", cg.Component)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(MobileFuelStations),
}).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await smart_display.register_plugin(var, __file__)
