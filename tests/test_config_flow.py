"""Tests for the Nest config flow."""
from homeassistant import data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.watts_vision import config_flow


async def test_data_entry_flow_form(hass: HomeAssistant):
    """Test we abort if no implementation is registered."""
    flow = config_flow.ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    # assert result["reason"] == "no_flows"


async def test_full_flow_implementation(hass: HomeAssistant):
    """Test registering an implementation and finishing flow works."""
    # gen_authorize_url = AsyncMock(return_value="https://example.com")
    # convert_code = AsyncMock(return_value={"access_token": "yoo"})

    # config_flow.register_flow_implementation(
    #     hass, "test", "Test", gen_authorize_url, convert_code
    # )
    # config_flow.register_flow_implementation(
    #     hass, "test-other", "Test Other", None, None
    # )

    flow = config_flow.ConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await flow.async_step_user({"username": "user", "password": "pass"})
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"base": "unknown"}

    # {
    #     'type': 'form',
    #     'flow_id': None,
    #     'handler': None,
    #     'step_id': 'user',
    #     'data_schema': <Schema({'username': <class 'str'>, 'password': <class 'str'>}, extra=PREVENT_EXTRA, required=False) object at 0x10aa688e0>,
    #     'errors': {'base': 'unknown'},
    #     'description_placeholders': None,
    #     'last_step': None
    # }
