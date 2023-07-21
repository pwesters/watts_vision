import functools
import logging
from typing import Callable

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_FAHRENHEIT
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    API_CLIENT,
    DOMAIN,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_DEFROST,
    PRESET_OFF,
    PRESET_PROGRAM,
    PRESET_MODE_MAP,
    PRESET_MODE_REVERSE_MAP,
)
from .watts_api import WattsApi

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: ConfigEntry,
    async_add_entities: Callable
):
    """Set up the climate platform."""

    wattsClient: WattsApi = hass.data[DOMAIN][API_CLIENT]

    smartHomes = wattsClient.getSmartHomes()

    devices = []

    if smartHomes is not None:
        for y in range(len(smartHomes)):
            if smartHomes[y]["zones"] is not None:
                for z in range(len(smartHomes[y]["zones"])):
                    if smartHomes[y]["zones"][z]["devices"] is not None:
                        for x in range(len(smartHomes[y]["zones"][z]["devices"])):
                            devices.append(
                                WattsThermostat(
                                    wattsClient,
                                    smartHomes[y]["smarthome_id"],
                                    smartHomes[y]["zones"][z]["devices"][x]["id"],
                                    smartHomes[y]["zones"][z]["devices"][x]["id_device"],
                                    smartHomes[y]["zones"][z]["zone_label"]
                                )
                            )

    async_add_entities(devices, update_before_add=True)


class WattsThermostat(ClimateEntity):
    """"""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str, deviceID: str, zone: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self.zone = zone
        self.deviceID = deviceID
        self._name = "Thermostat " + zone
        self._available = True
        self._attr_extra_state_attributes = {"previous_gv_mode": "0"}

    @property
    def unique_id(self):
        """Return the unique ID for this device."""
        return "watts_thermostat_" + self.id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

    @property
    def temperature_unit(self) -> str:
        return TEMP_FAHRENHEIT

    @property
    def hvac_modes(self) -> list[str]:
        return [HVAC_MODE_HEAT] + [HVAC_MODE_COOL] + [HVAC_MODE_OFF]

    @property
    def hvac_mode(self) -> str:
        return self._attr_hvac_mode

    @property
    def hvac_action(self) -> str:
        return self._attr_hvac_action

    @property
    def preset_modes(self) -> list[str]:
        """Return the available presets."""
        return list(PRESET_MODE_MAP.values())

    @property
    def preset_mode(self) -> str:
        return self._attr_preset_mode

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.id)
            },
            "manufacturer": "Watts",
            "name": "Thermostat " + self.zone,
            "model": "BT-D03-RF",
            "via_device": (DOMAIN, self.smartHome)
        }

    async def async_update(self):
        # try:
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)

        self._attr_current_temperature = float(smartHomeDevice["temperature_air"]) / 10
        if smartHomeDevice["gv_mode"] != "2":
            self._attr_min_temp = float(smartHomeDevice["min_set_point"]) / 10
            self._attr_max_temp = float(smartHomeDevice["max_set_point"]) / 10
        else:
            self._attr_min_temp = float(446 / 10)
            self._attr_max_temp = float(446 / 10)

        if smartHomeDevice["heating_up"] == "0":
            if smartHomeDevice["gv_mode"] == "1":
                self._attr_hvac_action = CURRENT_HVAC_OFF
            else:
                self._attr_hvac_action = CURRENT_HVAC_IDLE
        else:
            if smartHomeDevice["heat_cool"] == "1":
                self._attr_hvac_action = CURRENT_HVAC_COOL
            else:
                self._attr_hvac_action = CURRENT_HVAC_HEAT

        if smartHomeDevice["gv_mode"] == "0":
            if smartHomeDevice["heat_cool"] == "1":
                self._attr_hvac_mode = HVAC_MODE_COOL
            else:
                self._attr_hvac_mode = HVAC_MODE_HEAT
            self._attr_preset_mode = PRESET_MODE_MAP["0"]
            self._attr_target_temperature = (
                float(smartHomeDevice["consigne_confort"]) / 10
            )
        if smartHomeDevice["gv_mode"] == "1":
            self._attr_hvac_mode = HVAC_MODE_OFF
            self._attr_preset_mode = PRESET_MODE_MAP["1"]
            self._attr_target_temperature = None
        if smartHomeDevice["gv_mode"] == "2":
            if smartHomeDevice["heat_cool"] == "1":
                self._attr_hvac_mode = HVAC_MODE_COOL
            else:
                self._attr_hvac_mode = HVAC_MODE_HEAT
            self._attr_preset_mode = PRESET_MODE_MAP["2"]
            self._attr_target_temperature = float(smartHomeDevice["consigne_hg"]) / 10
        if smartHomeDevice["gv_mode"] == "3":
            if smartHomeDevice["heat_cool"] == "1":
                self._attr_hvac_mode = HVAC_MODE_COOL
            else:
                self._attr_hvac_mode = HVAC_MODE_HEAT
            self._attr_preset_mode = PRESET_MODE_MAP["3"]
            self._attr_target_temperature = float(smartHomeDevice["consigne_eco"]) / 10
        if smartHomeDevice["gv_mode"] == "4":
            if smartHomeDevice["heat_cool"] == "1":
                self._attr_hvac_mode = HVAC_MODE_COOL
            else:
                self._attr_hvac_mode = HVAC_MODE_HEAT
            self._attr_preset_mode = PRESET_MODE_MAP["4"]
            self._attr_target_temperature = (
                float(smartHomeDevice["consigne_boost"]) / 10
            )
        if smartHomeDevice["gv_mode"] == "11":
            if smartHomeDevice["heat_cool"] == "1":
                self._attr_hvac_mode = HVAC_MODE_COOL
            else:
                self._attr_hvac_mode = HVAC_MODE_HEAT
            self._attr_preset_mode = PRESET_MODE_MAP["11"]
            self._attr_target_temperature = (
                float(smartHomeDevice["consigne_manuel"]) / 10
            )

        self._attr_extra_state_attributes["consigne_confort"] = (
            float(smartHomeDevice["consigne_confort"]) / 10
        )
        self._attr_extra_state_attributes["consigne_hg"] = (
            float(smartHomeDevice["consigne_hg"]) / 10
        )
        self._attr_extra_state_attributes["consigne_eco"] = (
            float(smartHomeDevice["consigne_eco"]) / 10
        )
        self._attr_extra_state_attributes["consigne_boost"] = (
            float(smartHomeDevice["consigne_boost"]) / 10
        )
        self._attr_extra_state_attributes["consigne_manuel"] = (
            float(smartHomeDevice["consigne_manuel"]) / 10
        )
        self._attr_extra_state_attributes["gv_mode"] = smartHomeDevice["gv_mode"]

        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT or hvac_mode == HVAC_MODE_COOL:
            value = "0"
            if self._attr_extra_state_attributes["previous_gv_mode"] == "0":
                value = str(int(self._attr_extra_state_attributes["consigne_confort"] * 10))
            elif self._attr_extra_state_attributes["previous_gv_mode"] == "2":
                value = str(int(self._attr_extra_state_attributes["consigne_hg"] * 10))
            elif self._attr_extra_state_attributes["previous_gv_mode"] == "3":
                value = str(int(self._attr_extra_state_attributes["consigne_eco"] * 10))
            elif self._attr_extra_state_attributes["previous_gv_mode"] == "4":
                value = str(int(self._attr_extra_state_attributes["consigne_boost"] * 10))
            elif self._attr_extra_state_attributes["previous_gv_mode"] == "11":
                value = str(int(self._attr_extra_state_attributes["consigne_manuel"] * 10))

            # reloading the devices may take some time, meanwhile set the new values manually
            for y in range(len(self.client._smartHomeData)):
                if self.client._smartHomeData[y]["smarthome_id"] == self.smartHome:
                    for z in range(len(self.client._smartHomeData[y]["zones"])):
                        for x in range(len(self.client._smartHomeData[y]["zones"][z]["devices"])):
                            if (self.client._smartHomeData[y]["zones"][z]["devices"][x]["id"] == self.id):
                                self.client._smartHomeData[y]["zones"][z]["devices"][x]["gv_mode"] = self._attr_extra_state_attributes["previous_gv_mode"]
                                self.client._smartHomeData[y]["zones"][z]["devices"][x]["consigne_manuel"] = value
                                if (self._attr_extra_state_attributes["previous_gv_mode"] == "0"):
                                    self._attr_extra_state_attributes["consigne_confort"] = value
                                elif (self._attr_extra_state_attributes["previous_gv_mode"] == "2"):
                                    self._attr_extra_state_attributes["consigne_hg"] = value
                                elif (self._attr_extra_state_attributes["previous_gv_mode"] == "3"):
                                    self._attr_extra_state_attributes["consigne_eco"] = value
                                elif (self._attr_extra_state_attributes["previous_gv_mode"] == "4"):
                                    self._attr_extra_state_attributes["consigne_boost"] = value

            func = functools.partial(
                self.client.pushTemperature,
                self.smartHome,
                self.deviceID,
                value,
                self._attr_extra_state_attributes["previous_gv_mode"]
            )
            await self.hass.async_add_executor_job(func)

        if hvac_mode == HVAC_MODE_OFF:
            self._attr_extra_state_attributes["previous_gv_mode"] = self._attr_extra_state_attributes["gv_mode"]

            # reloading the devices may take some time, meanwhile set the new values manually
            for y in range(len(self.client._smartHomeData)):
                if self.client._smartHomeData[y]["smarthome_id"] == self.smartHome:
                    for z in range(len(self.client._smartHomeData[y]["zones"])):
                        for x in range(len(self.client._smartHomeData[y]["zones"][z]["devices"])):
                            if (self.client._smartHomeData[y]["zones"][z]["devices"][x]["id"] == self.id):
                                self.client._smartHomeData[y]["zones"][z]["devices"][x]["gv_mode"] = PRESET_MODE_REVERSE_MAP[PRESET_OFF]
                                self.client._smartHomeData[y]["zones"][z]["devices"][x]["consigne_manuel"] = "0"

            func = functools.partial(
                self.client.pushTemperature,
                self.smartHome,
                self.deviceID,
                "0",
                PRESET_MODE_REVERSE_MAP[PRESET_OFF]
            )
            await self.hass.async_add_executor_job(func)

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        value = 0
        if preset_mode != PRESET_OFF:
            if preset_mode == PRESET_DEFROST:
                value = str(int(self._attr_extra_state_attributes["consigne_hg"] * 10))
            elif preset_mode == PRESET_ECO:
                value = str(int(self._attr_extra_state_attributes["consigne_eco"] * 10))
            elif preset_mode == PRESET_BOOST:
                value = str(int(self._attr_extra_state_attributes["consigne_boost"] * 10))
            elif preset_mode == PRESET_PROGRAM:
                value = str(int(self._attr_extra_state_attributes["consigne_manuel"] * 10))
            else:
                value = str(int(self._attr_extra_state_attributes["consigne_confort"] * 10))
        else:
            self._attr_extra_state_attributes["previous_gv_mode"] = self._attr_extra_state_attributes["gv_mode"]

        # reloading the devices may take some time, meanwhile set the new values manually
        for y in range(len(self.client._smartHomeData)):
            if self.client._smartHomeData[y]["smarthome_id"] == self.smartHome:
                for z in range(len(self.client._smartHomeData[y]["zones"])):
                    for x in range(len(self.client._smartHomeData[y]["zones"][z]["devices"])):
                        if (self.client._smartHomeData[y]["zone"][z]["devices"][x]["id"] == self.id):
                            self.client._smartHomeData[y]["zone"][z]["devices"][x]["gv_mode"] = PRESET_MODE_REVERSE_MAP[preset_mode]
                            self.client._smartHomeData[y]["zone"][z]["devices"][x]["consigne_manuel"] = value

        func = functools.partial(
            self.client.pushTemperature,
            self.smartHome,
            self.deviceID,
            value,
            PRESET_MODE_REVERSE_MAP[preset_mode]
        )
        await self.hass.async_add_executor_job(func)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        value = str(int(kwargs["temperature"] * 10))
        gvMode = PRESET_MODE_REVERSE_MAP[self._attr_preset_mode]

        # Get the smartHomeDevice
        smartHomeDevice = self.client.getDevice(self.smartHome, self.id)

        # update its temp settings
        smartHomeDevice["consigne_manuel"] = value
        smartHomeDevice["consigne_confort"] = value

        # Set the smartHomeDevice using the just altered SmartHomeDevice
        self.client.setDevice(self.smartHome, self.id, smartHomeDevice)

        func = functools.partial(
            self.client.pushTemperature,
            self.smartHome,
            self.deviceID,
            value,
            gvMode
        )

        await self.hass.async_add_executor_job(func)
