"""Watts Vision sensor platform."""
from datetime import timedelta
import logging
import math
from typing import Callable, Optional

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.helpers.typing import HomeAssistantType
from numpy import NaN

from .const import API_CLIENT, DOMAIN
from .watts_api import WattsApi
from .central_unit import WattsVisionLastCommunicationSensor

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: ConfigEntry,
    async_add_entities: Callable
):
    """Set up the sensor platform."""

    wattsClient: WattsApi = hass.data[DOMAIN][API_CLIENT]

    smartHomes = wattsClient.getSmartHomes()

    sensors = []

    if smartHomes is not None:
        for y in range(len(smartHomes)):
            if smartHomes[y]["zones"] is not None:
                for z in range(len(smartHomes[y]["zones"])):
                    if smartHomes[y]["zones"][z]["devices"] is not None:
                        for x in range(len(smartHomes[y]["zones"][z]["devices"])):
                            sensors.append(
                                WattsVisionThermostatSensor(
                                    wattsClient,
                                    smartHomes[y]["smarthome_id"],
                                    smartHomes[y]["zones"][z]["devices"][x]["id"],
                                    smartHomes[y]["zones"][z]["zone_label"]
                                )
                            )
                            sensors.append(
                                WattsVisionTemperatureSensor(
                                    wattsClient,
                                    smartHomes[y]["smarthome_id"],
                                    smartHomes[y]["zones"][z]["devices"][x]["id"],
                                    smartHomes[y]["zones"][z]["zone_label"]
                                )
                            )
                            sensors.append(
                                WattsVisionSetTemperatureSensor(
                                    wattsClient,
                                    smartHomes[y]["smarthome_id"],
                                    smartHomes[y]["zones"][z]["devices"][x]["id"],
                                    smartHomes[y]["zones"][z]["zone_label"]
                                )
                            )
            sensors.append(
                WattsVisionLastCommunicationSensor(
                    wattsClient,
                    smartHomes[y]["smarthome_id"],
                    smartHomes[y]["label"]
                )
            )

    async_add_entities(sensors, update_before_add=True)


class WattsVisionThermostatSensor(SensorEntity):
    """Representation of a Watts Vision thermostat."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str, zone: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self.zone = zone
        self._name = "Heating mode " + zone
        self._state = None
        self._available = True

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "thermostat_mode_" + self.id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.id)
            },
            "manufacturer": "Watts",
            "name": "Thermostat" + self.zone,
            "model": "BT-D03-RF",
            "via_device": (DOMAIN, self.smartHome)
        }

    async def async_update(self):
        # try:
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)

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

        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")


class WattsVisionTemperatureSensor(SensorEntity):
    """Representation of a Watts Vision temperature sensor."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str, zone: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self.zone = zone
        self._name = "Air temperature " + zone
        self._state = None
        self._available = True

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "temperature_air_" + self.id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        return TEMP_FAHRENHEIT

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.id)
            },
            "manufacturer": "Watts",
            "name": "Thermostat" + self.zone,
            "model": "BT-D03-RF",
            "via_device": (DOMAIN, self.smartHome)
        }

    async def async_update(self):
        # try:
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
            self._state = math.floor(((float(smartHomeDevice["temperature_air"]) / 10) - 32) / 1.8 * 10) / 10
        else:
            self._state = float(smartHomeDevice["temperature_air"]) / 10
        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")


class WattsVisionSetTemperatureSensor(SensorEntity):
    """Representation of a Watts Vision temperature sensor."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str, zone: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self.zone = zone
        self._name = "Target temperature " + zone
        self._state = None
        self._available = True

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "target_temperature_" + self.id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        return TEMP_FAHRENHEIT

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.id)
            },
            "manufacturer": "Watts",
            "name": "Thermostat" + self.zone,
            "model": "BT-D03-RF",
            "via_device": (DOMAIN, self.smartHome)
        }

    async def async_update(self):
        # try:
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)

        if smartHomeDevice["gv_mode"] == "0":
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
                self._state = math.floor(((float(smartHomeDevice["consigne_confort"]) / 10) - 32) / 1.8 * 10) / 10
            else: 
                self._state = float(smartHomeDevice["consigne_confort"]) / 10
        if smartHomeDevice["gv_mode"] == "1":
            self._state = NaN
        if smartHomeDevice["gv_mode"] == "2":
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
                self._state = math.floor(((float(smartHomeDevice["consigne_hg"]) / 10) - 32) / 1.8 * 10) / 10
            else: 
                self._state = float(smartHomeDevice["consigne_hg"]) / 10
        if smartHomeDevice["gv_mode"] == "3":
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
                self._state = math.floor(((float(smartHomeDevice["consigne_eco"]) / 10) - 32) / 1.8 * 10) / 10
            else: 
                self._state = float(smartHomeDevice["consigne_eco"]) / 10
        if smartHomeDevice["gv_mode"] == "4":
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
                self._state = math.floor(((float(smartHomeDevice["consigne_boost"]) / 10) - 32) / 1.8 * 10) / 10
            else: 
                self._state = float(smartHomeDevice["consigne_boost"]) / 10
        if smartHomeDevice["gv_mode"] == "11":
            if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
                self._state = math.floor(((float(smartHomeDevice["consigne_manuel"]) / 10) - 32) / 1.8 * 10) / 10
            else: 
                self._state = float(smartHomeDevice["consigne_manuel"]) / 10

        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")
