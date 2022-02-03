import functools
import logging
import requests

from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

class WattsApi:
    """Interface to the SEMS API."""

    def __init__(self, hass, username, password):
        """Init dummy hub."""
        self._hass = hass
        self._username = username
        self._password = password
        self._token = None
        self._refresh_token = None
    
    async def test_authentication(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            token = await self.getLoginToken()
            return token is not None
        except:
            _LOGGER.exception("Watts Authentication exception")
            return False
    
    async def getLoginToken(self):
        """Get the login token for the Watts Smarthome API"""

        payload = { 
            'grant_type': 'password', 
            'username': self._username,
            'password': self._password, 
            'client_id': 'app-front' 
        }
        func = functools.partial(
            requests.post,
            url = "https://smarthome.wattselectronics.com/auth/realms/watts/protocol/openid-connect/token",
            data = payload
        )
        request_token_result = await self._hass.async_add_executor_job(func)

        if request_token_result.status_code == 200:
            token = request_token_result.json()['access_token']
            self._token = token
            self._refresh_token = request_token_result.json()['refresh_token']
            return token
        else:
            _LOGGER.error("Something went wrong fetching token: {0}".format(request_token_result.status_code))
            raise None

    async def getSmartHomes(self, firstTry = True):
        """Get the user data"""

        headers = { 
            'Authorization': 'Bearer {}'.format(self._token) 
        }
        payload = { 
            'token': 'true', 
            'email': self._username, 
            'lang': 'nl_NL' 
        }
        func = functools.partial(
            requests.post,
            url = 'https://smarthome.wattselectronics.com/api/v0.1/human/user/read/',
            headers = headers, 
            data = payload
        )

        user_data_result = await self._hass.async_add_executor_job(func)

        if user_data_result.status_code == 200:
            if user_data_result.json()['code']['code'] == '1' and user_data_result.json()['code']['key'] == 'OK' and user_data_result.json()['code']['value'] == 'OK':
                return user_data_result.json()['data']['smarthomes']
            else:
                if firstTry:
                    """Token may be expired, try to fetch new token"""
                    token = await self.getLoginToken()
                    return await self.getSmartHomes(firstTry=False)
                else:
                    _LOGGER.error("Something went wrong fetching user data./nCode: {0}, Key: {1}, Value: {2}".format(user_data_result.json()['code']['code'], user_data_result.json()['code']['key'], user_data_result.json()['code']['value']))
                    return None
        else:
            _LOGGER.error("Something went wrong fetching user data: {0}".format(user_data_result.status_code))
            return None
    
    async def getDevices(self, smarthome, firstTry = True):
        """Get devices for smart home"""

        headers = { 
            'Authorization': 'Bearer {}'.format(self._token) 
        }
        payload = { 
            'token': 'true', 
            'smarthome_id': smarthome, 
            'lang': 'nl_NL' 
        }
        func = functools.partial(
            requests.post,
            url = 'https://smarthome.wattselectronics.com/api/v0.1/human/smarthome/read',
            headers = headers, 
            data = payload
        )

        devices_result = await self._hass.async_add_executor_job(func)

        if devices_result.status_code == 200:
            if devices_result.json()['code']['code'] == '1' and devices_result.json()['code']['key'] == 'OK' and devices_result.json()['code']['value'] == 'OK':
                
                return devices_result.json()['data']['devices']
            else:
                if firstTry:
                    """Token may be expired, try to fetch new token"""
                    token = await self.getLoginToken()
                    return await self.getDevices(smarthome, firstTry=False)
                else:
                    _LOGGER.error("Something went wrong fetching user data./nCode: {0}, Key: {1}, Value: {2}".format(devices_result.json()['code']['code'], devices_result.json()['code']['key'], devices_result.json()['code']['value']))
                    return None
        else:
            _LOGGER.error("Something went wrong fetching devices: {0}".format(devices_result.status_code))
            return None
    
    async def getDevice(self, smarthome, deviceId, firstTry = True):
        """Get specific device"""

        headers = { 
            'Authorization': 'Bearer {}'.format(self._token) 
        }
        payload = { 
            'token': 'true', 
            'smarthome_id': smarthome, 
            'lang': 'nl_NL' 
        }
        func = functools.partial(
            requests.post,
            url = 'https://smarthome.wattselectronics.com/api/v0.1/human/smarthome/read',
            headers = headers, 
            data = payload
        )

        devices_result = await self._hass.async_add_executor_job(func)

        if devices_result.status_code == 200:
            if devices_result.json()['code']['code'] == '1' and devices_result.json()['code']['key'] == 'OK' and devices_result.json()['code']['value'] == 'OK':
                for y in range(len(devices_result.json()['data']['devices'])):
                    if devices_result.json()['data']['devices'][str(y)]['id'] == deviceId:
                        return devices_result.json()['data']['devices'][str(y)]
            else:
                if firstTry:
                    """Token may be expired, try to fetch new token"""
                    token = await self.getLoginToken()
                    return await self.getDevice(smarthome, deviceId, firstTry=False)
                else:
                    _LOGGER.error("Something went wrong fetching user data./nCode: {0}, Key: {1}, Value: {2}".format(devices_result.json()['code']['code'], devices_result.json()['code']['key'], devices_result.json()['code']['value']))
                    return None
        else:
            _LOGGER.error("Something went wrong fetching devices: {0}".format(devices_result.status_code))
            return None

