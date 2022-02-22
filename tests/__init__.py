"""Testing for Watts Vision Component."""
# import json
# from unittest.mock import patch

# from homeassistant.const import CONF_HOST, CONF_TYPE
# from homeassistant.core import HomeAssistant
# from pytest_homeassistant_custom_component.common import (  # , load_fixture
#     MockConfigEntry,
# )

# from custom_components.watts_vision.const import DOMAIN


# async def init_integration(hass: HomeAssistant, skip_setup=False) -> MockConfigEntry:
#     self.async_create_entry(title="Watts Vision", data=user_input)

#     """Set up the Brother integration in Home Assistant."""
#     entry = MockConfigEntry(
#         domain=DOMAIN,
#         title="HL-L2340DW 0123456789",
#         unique_id="0123456789",
#         data={CONF_HOST: "localhost", CONF_TYPE: "laser"},
#     )

#     entry.add_to_hass(hass)

#     # if not skip_setup:
#     #     with patch(
#     #         "brother.Brother._get_data",
#     #         return_value=json.loads(load_fixture("printer_data.json", "brother")),
#     #     ):
#     #         await hass.config_entries.async_setup(entry.entry_id)
#     #         await hass.async_block_till_done()

#     return entry
