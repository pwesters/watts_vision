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

    hass.data[DOMAIN][CONF_USERNAME] = config[DOMAIN].get(CONF_USERNAME)
    hass.data[DOMAIN][CONF_PASSWORD] = config[DOMAIN].get(CONF_PASSWORD)

    for platform in PLATFORMS:
        # hass.async_create_task(
        #     hass.config_entries.async_forward_entry_setup(entry, platform)
        # )
        load_platform(hass, platform, DOMAIN, {}, config)

    return True
