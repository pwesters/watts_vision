import logging
from numpy import NaN
from typing import Callable, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE
)
from homeassistant.const import (
    TEMP_FAHRENHEIT
)
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .watts_api import WattsApi

from .const import (
    DOMAIN,
    PRESET_DEFROST,
    PRESET_OFF,
    PRESET_PROGRAM
)

_LOGGER = logging.getLogger(__name__)


PRESET_MODE_MAP = {
    "0": PRESET_COMFORT,
    "1": PRESET_OFF,
    "2": PRESET_DEFROST,
    "3": PRESET_ECO,
    "4": PRESET_BOOST,
    "11": PRESET_PROGRAM
}

PRESET_MODE_REVERSE_MAP = {
    PRESET_COMFORT: "0",
    PRESET_OFF: "1",
    PRESET_DEFROST: "2",
    PRESET_ECO: "3",
    PRESET_BOOST: "4",
    PRESET_PROGRAM: "11"
}

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the climate platform."""

    wattsClient: WattsApi = hass.data[DOMAIN]['api']
    
    smartHomes = wattsClient.getSmartHomes()

    devices = []

    for y in range(len(smartHomes)):
        for x in range(len(smartHomes[str(y)]['devices'])):
            devices.append(
                WattsThermostat(
                    wattsClient, 
                    smartHomes[str(y)]['smarthome_id'], 
                    smartHomes[str(y)]['devices'][str(x)]['id'],
                    smartHomes[str(y)]['devices'][str(x)]['id_device']
                )
            )
    
    async_add_entities(devices, update_before_add=True)


class WattsThermostat(ClimateEntity):
    """"""
    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str, deviceID: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self.deviceID = deviceID
        self._name = "watts_thermostat"
        self._available = True
    
    @property
    def unique_id(self):
        """Return the unique ID for this device."""
        return "watts_thermostat_" + self.id
    
    @property
    def supported_features(self):
        return (
            SUPPORT_TARGET_TEMPERATURE
            | SUPPORT_PRESET_MODE
        )
    
    @property
    def temperature_unit(self):
        return TEMP_FAHRENHEIT
    
    @property
    def hvac_modes(self):
        return [HVAC_MODE_HEAT] + [HVAC_MODE_OFF]
    
    @property
    def preset_modes(self) -> list[str]:
        """Return the available presets."""
        modes = []
        modes.append(PRESET_MODE_MAP["0"])
        modes.append(PRESET_MODE_MAP["1"])
        modes.append(PRESET_MODE_MAP["2"])
        modes.append(PRESET_MODE_MAP["3"])
        modes.append(PRESET_MODE_MAP["4"])
        modes.append(PRESET_MODE_MAP["11"])
        return modes
    
    async def async_update(self):
        try:
            smartHomeDevice = await self.client.getDevice(self.smartHome, self.id)

            self._attr_current_temperature = float(smartHomeDevice["temperature_air"]) / 10
            if smartHomeDevice["gv_mode"] != "2":
                self._attr_min_temp = float(smartHomeDevice["min_set_point"]) / 10
                self._attr_max_temp = float(smartHomeDevice["max_set_point"]) / 10
            else:
                self._attr_min_temp = float(446)
                self._attr_max_temp = float(446)

            if smartHomeDevice["heating_up"] == '0':
                if smartHomeDevice["gv_mode"] == "1":
                    self._attr_hvac_action = CURRENT_HVAC_OFF
                else:
                    self._attr_hvac_action = CURRENT_HVAC_IDLE
            else:
                self._attr_hvac_action = CURRENT_HVAC_HEAT
            
            if smartHomeDevice["gv_mode"] == "0":
                self._attr_hvac_mode = HVAC_MODE_HEAT
                self._attr_preset_mode = PRESET_MODE_MAP["0"]
                self._attr_target_temperature = float(smartHomeDevice["consigne_confort"]) / 10
            if smartHomeDevice["gv_mode"] == "1":
                self._attr_hvac_mode = HVAC_MODE_OFF
                self._attr_preset_mode = PRESET_MODE_MAP["1"]
                self._attr_target_temperature = NaN
            if smartHomeDevice["gv_mode"] == "2":
                self._attr_hvac_mode = HVAC_MODE_HEAT
                self._attr_preset_mode = PRESET_MODE_MAP["2"]
                self._attr_target_temperature = float(smartHomeDevice["consigne_hg"]) / 10
            if smartHomeDevice["gv_mode"] == "3":
                self._attr_hvac_mode = HVAC_MODE_HEAT
                self._attr_preset_mode = PRESET_MODE_MAP["3"]
                self._attr_target_temperature = float(smartHomeDevice["consigne_eco"]) / 10
            if smartHomeDevice["gv_mode"] == "4":
                self._attr_hvac_mode = HVAC_MODE_HEAT
                self._attr_preset_mode = PRESET_MODE_MAP["4"]
                self._attr_target_temperature = float(smartHomeDevice["consigne_boost"]) / 10
            if smartHomeDevice["gv_mode"] == "11":
                self._attr_hvac_mode = HVAC_MODE_HEAT
                self._attr_preset_mode = PRESET_MODE_MAP["11"]
                self._attr_target_temperature = float(smartHomeDevice["consigne_manuel"]) / 10
            
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data.")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.warning(hvac_mode)

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        _LOGGER.warning(preset_mode)
    
    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        value = str(int(kwargs['temperature'] * 10))
        gvMode = PRESET_MODE_REVERSE_MAP[self._attr_preset_mode]
        await self.client.pushTemperature(self.smartHome, self.deviceID, value, gvMode)
