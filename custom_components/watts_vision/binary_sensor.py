from datetime import timedelta
import logging
from typing import Callable, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up the binary_sensor platform."""
    wattsClient: WattsApi = hass.data[DOMAIN]["api"]

    smartHomes = wattsClient.getSmartHomes()

    sensors = []

    if smartHomes is not None:
        for y in range(len(smartHomes)):
            if smartHomes[str(y)]["devices"] is not None:
                for x in range(len(smartHomes[str(y)]["devices"])):
                    sensors.append(
                        WattsVisionHeatingBinarySensor(
                            wattsClient,
                            smartHomes[str(y)]["smarthome_id"],
                            smartHomes[str(y)]["devices"][str(x)]["id"],
                        )
                    )

    async_add_entities(sensors, update_before_add=True)


class WattsVisionHeatingBinarySensor(BinarySensorEntity):
    """Representation of a Watts Vision thermostat."""

    def __init__(self, wattsClient: WattsApi, smartHome: str, id: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self.id = id
        self._name = "watts_vision_"
        self._state: bool = False
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name + "is_heating"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "thermostat_is_heating_" + self.id

    @property
    def device_id(self) -> str:
        return "watts_vision_watts_thermostat_" + self.id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        # try:
        smartHomeDevice = await self.client.getDevice(self.smartHome, self.id)
        if smartHomeDevice["heating_up"] == "0":
            self._state = False
        else:
            self._state = True
        # except:
        #     self._available = False
        #     _LOGGER.exception("Error retrieving data.")
