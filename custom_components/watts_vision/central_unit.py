"""Watts Vision sensor platform -- central unit."""
from typing import Optional
from .const import DOMAIN
from .watts_api import WattsApi
from homeassistant.components.sensor import SensorEntity


class WattsVisionLastCommunicationSensor(SensorEntity):
    def __init__(self, wattsClient: WattsApi, smartHome: str, label: str):
        super().__init__()
        self.client = wattsClient
        self.smartHome = smartHome
        self._label = label
        self._name = "Last communication " + self._label
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
            "name": "Central Unit " + self._label,
            "model": "BT-CT02-RF"
        }

    async def async_update(self):
        data = await self.hass.async_add_executor_job(self.client.getLastCommunication, self.smartHome)

        self._state = "{} days, {} hours, {} minutes and {} seconds.".format(
            data["diffObj"]["days"],
            data["diffObj"]["hours"],
            data["diffObj"]["minutes"],
            data["diffObj"]["seconds"]
        )
