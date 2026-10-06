"""Constants for Mobile Fuel Stations."""

from datetime import timedelta

DOMAIN = "mobile_fuel_stations"
CONFIG_ENTRY_VERSION = 2
FRONTEND_VERSION = "0.5.0-beta.5"
FRONTEND_FILENAME = "mobile-fuel-stations-card.js"
FRONTEND_URL = f"/{DOMAIN}/{FRONTEND_FILENAME}?v={FRONTEND_VERSION}"
FRONTEND_RESOURCE_URL = FRONTEND_URL
PLATFORMS = ["sensor"]
CONF_API_KEY = "api_key"
CONF_TANKERKOENIG_API_KEY = "tankerkoenig_api_key"
CONF_PETROMAP_API_KEY = "petromap_api_key"
CONF_PETROMAP_PRIVACY_ACCEPTED = "petromap_privacy_accepted"
CONF_NAKORDONI_API_KEY = "nakordoni_api_key"
CONF_NAKORDONI_PRIVACY_ACCEPTED = "nakordoni_privacy_accepted"
CONF_PROVIDER_MODE = "provider_mode"
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
PROVIDER_TANKERKOENIG = "tankerkoenig"
PROVIDER_PETROMAP = "petromap"
PROVIDER_AUTO = "auto"
PROVIDER_NAKORDONI = "nakordoni"
MIN_UPDATE_INTERVAL = 5
API_URL = "https://creativecommons.tankerkoenig.de/json/list.php"
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.state"

DEFAULT_TIMEOUT = timedelta(seconds=15)
MAX_API_RADIUS_KM = 25.0
