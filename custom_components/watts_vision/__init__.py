"""Watts Vision Component."""

import logging
from datetime import timedelta
import voluptuous as vol

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.helpers.event import async_track_time_interval

from custom_components.watts_vision.watts_api import WattsApi

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["sensor"]

SCAN_INTERVAL = timedelta(seconds=120)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Watts component from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})

    client = WattsApi(hass, config[DOMAIN].get(CONF_USERNAME), config[DOMAIN].get(CONF_PASSWORD))
    await client.loadData()

    hass.data[DOMAIN]['api'] = client

    for platform in PLATFORMS:
        load_platform(hass, platform, DOMAIN, {}, config)
    
    async def refresh_devices(event_time):
        await client.reloadDevices()
    
    async_track_time_interval(hass, refresh_devices, SCAN_INTERVAL)

    return True

# from homeassistant import core


# async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
#     """Set up the Watts Vision component."""
#     # @TODO: Add setup code.
#     return True
