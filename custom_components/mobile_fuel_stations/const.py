"""Constants for Mobile Fuel Stations."""

from datetime import timedelta

DOMAIN = "mobile_fuel_stations"
FRONTEND_VERSION = "0.2.0-beta.1"
FRONTEND_FILENAME = "mobile-fuel-stations-card.js"
FRONTEND_URL = f"/{DOMAIN}/{FRONTEND_FILENAME}"
FRONTEND_RESOURCE_URL = f"{FRONTEND_URL}?v={FRONTEND_VERSION}"
PLATFORMS = ["sensor"]
CONF_API_KEY = "api_key"
CONF_LOCATION_ENTITY = "location_entity"
CONF_RADIUS = "radius"
CONF_FUEL_TYPE = "fuel_type"
CONF_STATION_COUNT = "station_count"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_MOVEMENT_UPDATES = "movement_updates"
CONF_MOVEMENT_THRESHOLD = "movement_threshold"
CONF_COOLDOWN = "cooldown"

DEFAULT_RADIUS = 20.0
DEFAULT_FUEL_TYPE = "diesel"
DEFAULT_STATION_COUNT = 5
DEFAULT_UPDATE_INTERVAL = 15
DEFAULT_MOVEMENT_UPDATES = True
DEFAULT_MOVEMENT_THRESHOLD = 2.0
DEFAULT_COOLDOWN = 5
MIN_UPDATE_INTERVAL = 5
API_URL = "https://creativecommons.tankerkoenig.de/json/list.php"
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.state"

DEFAULT_TIMEOUT = timedelta(seconds=15)
