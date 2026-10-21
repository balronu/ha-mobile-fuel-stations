"""Constants for Mobile Fuel Stations."""

from datetime import timedelta

DOMAIN = "mobile_fuel_stations"
CONFIG_ENTRY_VERSION = 4
FRONTEND_VERSION = "0.8.4-beta.3"
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
CONF_NAKORDONI_AUTH_METHOD = "nakordoni_auth_method"
AUTH_METHOD_API_KEY = "api_key"
AUTH_METHOD_OAUTH2 = "oauth2"
NAKORDONI_OAUTH_CLIENT_ID = "nkd_30ad5daeb089abfc3c1ea20b"
NAKORDONI_OAUTH_AUTHORIZE_URL = "https://api.nakordoni.dev/oauth/authorize"
NAKORDONI_OAUTH_TOKEN_URL = "https://api.nakordoni.dev/oauth/token"
NAKORDONI_OAUTH_IMPLEMENTATION = "nakordoni"
NAKORDONI_MARKETS = frozenset(
    {"DE", "AT", "PL", "CZ", "SK", "HU", "SI", "HR", "IT", "FR", "BE", "NL", "LU"}
)
CONF_PROVIDER_MODE = "provider_mode"
CONF_PROVIDER_MODES = "provider_modes"
CONF_LOCATION_ENTITY = "location_entity"
CONF_RADIUS = "radius"
CONF_FUEL_TYPE = "fuel_type"
CONF_FUEL_TYPES = "fuel_types"
CONF_STATION_COUNT = "station_count"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_MOVEMENT_UPDATES = "movement_updates"
CONF_MOVEMENT_THRESHOLD = "movement_threshold"
CONF_COOLDOWN = "cooldown"
CONF_ADAPTIVE_UPDATES = "adaptive_updates"
CONF_SORT_MODE = "sort_mode"
CONF_SORT_FUEL = "sort_fuel"
CONF_MANAGE_CREDENTIALS = "manage_credentials"
CONF_PROVIDER_STATUS = "provider_status"
CONF_FETCH_MODE = "fetch_mode"

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
DEFAULT_ADAPTIVE_UPDATES = False
FETCH_MODE_AUTOMATIC = "automatic"
FETCH_MODE_MANUAL = "manual"
DEFAULT_FETCH_MODE = FETCH_MODE_AUTOMATIC
DEFAULT_ADAPTIVE_MOVEMENT_THRESHOLD_KM = 3.0
DEFAULT_SORT_MODE = "distance"
DEFAULT_SORT_FUEL = DEFAULT_FUEL_TYPE
PROVIDER_TANKERKOENIG = "tankerkoenig"
PROVIDER_PETROMAP = "petromap"
PROVIDER_AUTO = "auto"
PROVIDER_NAKORDONI = "nakordoni"
MIN_UPDATE_INTERVAL = 5
ADAPTIVE_STATIONARY_INTERVAL = timedelta(minutes=15)
ADAPTIVE_CITY_INTERVAL = timedelta(minutes=5)
ADAPTIVE_COUNTRY_ROAD_INTERVAL = timedelta(minutes=2)
ADAPTIVE_MOTORWAY_INTERVAL = timedelta(minutes=1)
API_URL = "https://creativecommons.tankerkoenig.de/json/list.php"
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.state"

DEFAULT_TIMEOUT = timedelta(seconds=15)
MAX_API_RADIUS_KM = 25.0
