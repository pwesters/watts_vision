"""Watts Vision sensor platform."""
from datetime import timedelta
import logging
from typing import Any, Callable, Dict, Optional
from numpy import NaN

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .const import DOMAIN
from .watts_api import WattsApi

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""

    wattsClient = hass.data[DOMAIN]['api']
    
    smartHomes = wattsClient.getSmartHomes()

    sensors = []

    for y in range(len(smartHomes)):
        for x in range(len(smartHomes[str(y)]['devices'])):
            sensors.append(WattsVisionThermostatSensor(wattsClient, smartHomes[str(y)]['smarthome_id'], smartHomes[str(y)]['devices'][str(x)]['id']))
            sensors.append(WattsVisionTemperatureSensor(wattsClient, smartHomes[str(y)]['smarthome_id'], smartHomes[str(y)]['devices'][str(x)]['id']))
            sensors.append(WattsVisionSetTemperatureSensor(wattsClient, smartHomes[str(y)]['smarthome_id'], smartHomes[str(y)]['devices'][str(x)]['id']))

    async_add_entities(sensors, update_before_add=True)


class WattsVisionThermostatSensor(Entity):
    """Representation of a Watts Vision thermostat."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, deviceID: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.deviceID = deviceID
        self.attrs: Dict[str, Any] = {}
        self._name = "watts_thermostat"
        self._state = None
        self._available = True
    
    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name + '_' + self.deviceID

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return 'thermostat_' + self.deviceID
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    # @property
    # def extra_state_attributes(self) -> Dict[str, Any]:
    #     return self.attrs
    
    async def async_update(self):
        try:
            smartHomeDevice = await self.client.getDevice(self.smartHome, self.deviceID)
            
            if smartHomeDevice["gv_mode"] == "0":
                self._state = "Comfort"
            if smartHomeDevice["gv_mode"] == "1":
                self._state = "Off"
            if smartHomeDevice["gv_mode"] == "2":
                self._state = "Frost protection"
            if smartHomeDevice["gv_mode"] == "3":
                self._state = "Eco"
            if smartHomeDevice["gv_mode"] == "4":
                self._state = "Boost"
            if smartHomeDevice["gv_mode"] == "11":
                self._state = "Program"
            
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data.")

class WattsVisionTemperatureSensor(Entity):
    """Representation of a Watts Vision temperature sensor."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, deviceID: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.deviceID = deviceID
        self.attrs: Dict[str, Any] = {}
        self._name = "watts_vision_"
        self._state = None
        self._available = True
    
    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name + 'temperature_' + self.deviceID

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return 'temperature_air_' + self.deviceID
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state
    
    @property
    def device_class(self):
        return "temperature"
    
    @property
    def native_unit_of_measurement(self):
        return "°F"
    
    @property
    def unit_of_measurement(self):
        return "°F"
    
    async def async_update(self):
        try:
            smartHomeDevice = await self.client.getDevice(self.smartHome, self.deviceID)
            self._state = int(smartHomeDevice["temperature_air"]) / 10
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data.")

class WattsVisionSetTemperatureSensor(Entity):
    """Representation of a Watts Vision temperature sensor."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, deviceID: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.deviceID = deviceID
        self.attrs: Dict[str, Any] = {}
        self._name = "watts_vision_"
        self._state = None
        self._available = True
    
    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name + 'set_temperature_' + self.deviceID

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return 'set_temperature_' + self.deviceID
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state
    
    @property
    def device_class(self):
        return "temperature"
    
    @property
    def native_unit_of_measurement(self):
        return "°F"
    
    @property
    def unit_of_measurement(self):
        return "°F"
    
    async def async_update(self):
        try:
            smartHomeDevice = await self.client.getDevice(self.smartHome, self.deviceID)

            if smartHomeDevice["gv_mode"] == "0":
                self._state = int(smartHomeDevice["consigne_confort"]) / 10
                # self._state = "Comfort"
            if smartHomeDevice["gv_mode"] == "1":
                self._state = NaN
                # self._state = "Off"
            if smartHomeDevice["gv_mode"] == "2":
                self._state = int(smartHomeDevice["consigne_hg"]) / 10
                # self._state = "Frost protection"
            if smartHomeDevice["gv_mode"] == "3":
                self._state = int(smartHomeDevice["consigne_eco"]) / 10
                # self._state = "Eco"
            if smartHomeDevice["gv_mode"] == "4":
                self._state = int(smartHomeDevice["consigne_boost"]) / 10
                #self._state = "Boost"
            if smartHomeDevice["gv_mode"] == "11":
                self._state = int(smartHomeDevice["consigne_manuel"]) / 10
                #self._state = "Program"

        except:
            self._available = False
            _LOGGER.exception("Error retrieving data.")
