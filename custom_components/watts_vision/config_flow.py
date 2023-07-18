"""
Config flow for Watts Vision integration.
"""
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import CONN_CLASS_CLOUD_POLL, ConfigFlow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol

from .const import DOMAIN
from .watts_api import WattsApi

CONFIG_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any], current: dict[str, Any] = None) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    # Check if the username already exists as an entry
    existing_entries = hass.config_entries.async_entries(DOMAIN)
    for entry in existing_entries:
        if entry.data.get(CONF_USERNAME) == data[CONF_USERNAME] and (current == None or entry.data.get(CONF_USERNAME) != current.get("username")):
            raise UsernameExists

    api = WattsApi(hass, data[CONF_USERNAME], data[CONF_PASSWORD])

    authenticated = await hass.async_add_executor_job(api.test_authentication)

    # If authentication fails, raise an exception.
    if not authenticated:
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return data


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Watts Vision."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input: dict[str, Any] = None):
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

        errors = {}

        try:
            _LOGGER.debug("Validate input")
            await validate_input(self.hass, user_input)
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except UsernameExists:
            errors["base"] = "username_exists"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title=str(user_input["username"]), data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

class UsernameExists(HomeAssistantError):
    """Error to indicate the username already exists."""

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the Watts Vision integration."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        updated = None
        if user_input is not None:
            try:
                _LOGGER.debug("Validate input")
                validated_data = await validate_input(self.hass, user_input, self.config_entry.data)

                # Update entry
                _LOGGER.debug("Updating entry")
                updated = self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    title=str(user_input["username"]),
                    data=validated_data,
                )
                if updated:
                    # Reload entry
                    _LOGGER.debug("Reloading entry")
                    await self.hass.config_entries.async_reload(
                        self.config_entry.entry_id
                    )

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except UsernameExists:
                errors["base"] = "username_exists"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # If updated, return to overview
                return self.async_create_entry(title="", data=None)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required(CONF_USERNAME, default=str(self.config_entry.data[CONF_USERNAME])): str,vol.Required(CONF_PASSWORD): str,}),
            errors=errors,
        )