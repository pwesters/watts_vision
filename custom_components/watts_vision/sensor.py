"""Watts Vision sensor platform."""
from datetime import timedelta
import logging
from typing import Callable, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from numpy import NaN

from .const import API_CLIENT, DOMAIN
from .watts_api import WattsApi

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
            if smartHomes[str(y)]["devices"] is not None:
                for x in range(len(smartHomes[str(y)]["devices"])):
                    sensors.append(
                        WattsVisionThermostatSensor(
                            wattsClient,
                            smartHomes[str(y)]["smarthome_id"],
                            smartHomes[str(y)]["devices"][str(x)]["id"],
                        )
                    )
                    sensors.append(
                        WattsVisionTemperatureSensor(
                            wattsClient,
                            smartHomes[str(y)]["smarthome_id"],
                            smartHomes[str(y)]["devices"][str(x)]["id"],
                        )
                    )
                    sensors.append(
                        WattsVisionSetTemperatureSensor(
                            wattsClient,
                            smartHomes[str(y)]["smarthome_id"],
                            smartHomes[str(y)]["devices"][str(x)]["id"],
                        )
                    )
            sensors.append(
                WattsVisionLastCommunicationSensor(
                    wattsClient,
                    smartHomes[str(y)]["smarthome_id"]
                )
            )

    async_add_entities(sensors, update_before_add=True)


class WattsVisionThermostatSensor(SensorEntity):
    """Representation of a Watts Vision thermostat."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self._name = "Heating mode"
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
            "name": "Thermostat",
            "model": "BT-D03-RF",
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

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self._name = "Air temperature"
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
        return "temperature"

    @property
    def native_unit_of_measurement(self):
        return "°F"

    @property
    def unit_of_measurement(self):
        return "°F"

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.id)
            },
            "manufacturer": "Watts",
            "name": "Thermostat",
            "model": "BT-D03-RF",
        }

    async def async_update(self):
        # try:
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)
        self._state = int(smartHomeDevice["temperature_air"]) / 10
        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")


class WattsVisionSetTemperatureSensor(SensorEntity):
    """Representation of a Watts Vision temperature sensor."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self._name = "Target temperature"
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
        return "temperature"

    @property
    def native_unit_of_measurement(self):
        return "°F"

    @property
    def unit_of_measurement(self):
        return "°F"

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.id)
            },
            "manufacturer": "Watts",
            "name": "Thermostat",
            "model": "BT-D03-RF",
        }

    async def async_update(self):
        # try:
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)

        if smartHomeDevice["gv_mode"] == "0":
            self._state = int(smartHomeDevice["consigne_confort"]) / 10
        if smartHomeDevice["gv_mode"] == "1":
            self._state = NaN
        if smartHomeDevice["gv_mode"] == "2":
            self._state = int(smartHomeDevice["consigne_hg"]) / 10
        if smartHomeDevice["gv_mode"] == "3":
            self._state = int(smartHomeDevice["consigne_eco"]) / 10
        if smartHomeDevice["gv_mode"] == "4":
            self._state = int(smartHomeDevice["consigne_boost"]) / 10
        if smartHomeDevice["gv_mode"] == "11":
            self._state = int(smartHomeDevice["consigne_manuel"]) / 10

        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")


class WattsVisionLastCommunicationSensor(SensorEntity):
    def __init__(self, wattsClient: WattsApi, smartHome: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self._name = "Last communication"
        self._state = None
        self._available = True

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "last_communication_" + self.smartHome

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
                (DOMAIN, self.smartHome)
            },
            "manufacturer": "Watts",
            "name": "Central Unit",
            "model": "BT-CT02-RF",
        }

    async def async_update(self):
        data = await self.hass.async_add_executor_job(self.client.getLastCommunication, self.smartHome)

        self._state = "{} days, {} hours, {} minutes and {} seconds.".format(
            data["diffObj"]["days"],
            data["diffObj"]["hours"],
            data["diffObj"]["minutes"],
            data["diffObj"]["seconds"]
        )
