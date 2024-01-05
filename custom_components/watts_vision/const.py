from datetime import timedelta

from homeassistant.components.climate.const import (
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
)

API_CLIENT = "api"

DOMAIN = "watts_vision"

PRESET_DEFROST = "Frost Protection"
PRESET_OFF = "Off"
PRESET_PROGRAM_ON = "Program on"
PRESET_PROGRAM_OFF = "Program off"

PRESET_MODE_MAP = {
    "0": PRESET_COMFORT,
    "1": PRESET_OFF,
    "2": PRESET_DEFROST,
    "3": PRESET_ECO,
    "4": PRESET_BOOST,
    "8": PRESET_PROGRAM_ON,
    "11": PRESET_PROGRAM_OFF,
}

PRESET_MODE_REVERSE_MAP = {
    PRESET_COMFORT: "0",
    PRESET_OFF: "1",
    PRESET_DEFROST: "2",
    PRESET_ECO: "3",
    PRESET_BOOST: "4",
    PRESET_PROGRAM_ON: "8",
    PRESET_PROGRAM_OFF: "11",
}

SCAN_INTERVAL = timedelta(seconds=120)

NO_ISSUES = "No issues"
DEF_BAT_TH = "Battery failure"

ERROR_MAP = {
    0: NO_ISSUES,
    1: DEF_BAT_TH
}

ERROR_REVERSE_MAP = {
    NO_ISSUES: 0,
    DEF_BAT_TH: 1
}
