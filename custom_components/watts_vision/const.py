from datetime import timedelta
from homeassistant.components.climate.const import (
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO
)

API_CLIENT = "api"

DOMAIN = "watts_vision"

PRESET_DEFROST = "Frost Protection"
PRESET_OFF = "Off"
PRESET_PROGRAM = "Program"

PRESET_MODE_MAP = {
    "0": PRESET_COMFORT,
    "1": PRESET_OFF,
    "2": PRESET_DEFROST,
    "3": PRESET_ECO,
    "4": PRESET_BOOST,
    "11": PRESET_PROGRAM,
}

PRESET_MODE_REVERSE_MAP = {
    PRESET_COMFORT: "0",
    PRESET_OFF: "1",
    PRESET_DEFROST: "2",
    PRESET_ECO: "3",
    PRESET_BOOST: "4",
    PRESET_PROGRAM: "11",
}

SCAN_INTERVAL = timedelta(seconds=120)
