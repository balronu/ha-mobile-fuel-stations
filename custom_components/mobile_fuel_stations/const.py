"""Constants for Mobile Fuel Stations."""

from datetime import timedelta

DOMAIN = "mobile_fuel_stations"
CONFIG_ENTRY_VERSION = 3
FRONTEND_VERSION = "0.5.0-beta.8"
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
CONF_FUEL_TYPES = "fuel_types"
CONF_STATION_COUNT = "station_count"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_MOVEMENT_UPDATES = "movement_updates"
CONF_MOVEMENT_THRESHOLD = "movement_threshold"
CONF_COOLDOWN = "cooldown"
CONF_SORT_MODE = "sort_mode"
CONF_SORT_FUEL = "sort_fuel"

DEFAULT_RADIUS = 20.0
DEFAULT_FUEL_TYPE = "diesel"
FUEL_TYPES = ("e5", "e10", "diesel", "lpg", "hvo100")
FUEL_TYPE_LABELS = {
    "e5": "Super E5",
    "e10": "Super E10",
    "diesel": "Diesel",
    "lpg": "Autogas LPG",
    "hvo100": "HVO100",
}
DEFAULT_STATION_COUNT = 5
DEFAULT_UPDATE_INTERVAL = 15
DEFAULT_MOVEMENT_UPDATES = True
DEFAULT_MOVEMENT_THRESHOLD = 2.0
DEFAULT_COOLDOWN = 5
DEFAULT_SORT_MODE = "distance"
DEFAULT_SORT_FUEL = DEFAULT_FUEL_TYPE
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
