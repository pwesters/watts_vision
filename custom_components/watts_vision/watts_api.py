from datetime import datetime, timedelta
import logging

from homeassistant.helpers.typing import HomeAssistantType
import requests

_LOGGER = logging.getLogger(__name__)


class WattsApi:
    """Interface to the Watts API."""

    def __init__(self, hass: HomeAssistantType, username: str, password: str):
        """Init dummy hub."""
        self._hass = hass
        self._username = username
        self._password = password
        self._token = None
        self._token_expires = None
        self._refresh_token = None
        self._refresh_expires_in = None
        self._smartHomeData = {}

    def test_authentication(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            token = self.getLoginToken(True)
            return token is not None
        except Exception as exception:
            _LOGGER.exception("Authentication exception {exception}")
            return False

    def getLoginToken(self, forcelogin = False):
        """Get the access token for the Watts Smarthome API through login or refresh"""

        now = datetime.now()

        if (forcelogin or not self._refresh_expires_in or self._refresh_expires_in <= now):
            _LOGGER.debug("Login to get an access token.")
            payload = {
                "grant_type": "password",
                "username": self._username,
                "password": self._password,
                "client_id": "app-front",
            }
        elif (self._token_expires <= now):
            _LOGGER.debug("Refreshing access token")
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": "app-front",
            }
        else:
            _LOGGER.debug("Getting token called unneeded.")

        request_token_result = requests.post(
            url="https://smarthome.wattselectronics.com/auth/realms/watts/protocol/openid-connect/token",
            data=payload,
        )

        if request_token_result.status_code == 200:
            token = request_token_result.json()["access_token"]
            self._token = token
            self._token_expires = now + timedelta(seconds=request_token_result.json()["expires_in"])
            self._refresh_token = request_token_result.json()["refresh_token"]
            self._refresh_expires_in = now + timedelta(seconds=request_token_result.json()["refresh_expires_in"])
            _LOGGER.debug("Received access token. New refresh_token needed on {}".format(self._refresh_expires_in))
            return token
        else:
            _LOGGER.error(
                "Something went wrong fetching the token: {}".format(
                    request_token_result.status_code
                )
            )
            raise None

    def loadData(self):
        """load data from api"""
        smarthomes = self.loadSmartHomes()
        self._smartHomeData = smarthomes

        return self.reloadDevices()

    def loadSmartHomes(self, firstTry: bool = True):
        """Load the user data"""
        self._refresh_token_if_expired()

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {"token": "true", "email": self._username, "lang": "nl_NL"}

        user_data_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/user/read/",
            headers=headers,
            data=payload,
        )

        if self.check_response(user_data_result):
            return user_data_result.json()["data"]["smarthomes"]

        return None

    def loadDevices(self, smarthome: str, firstTry: bool = True):
        """Load devices for smart home"""
        self._refresh_token_if_expired()

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {"token": "true", "smarthome_id": smarthome, "lang": "nl_NL"}

        devices_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/smarthome/read",
            headers=headers,
            data=payload,
        )

        if self.check_response(devices_result):
            return devices_result.json()["data"]["zones"]

        return None

    def _refresh_token_if_expired(self) -> None:
        """Check if token is expired and request a new one."""
        now = datetime.now()

        if (self._token_expires and self._token_expires <= now
            or
            self._refresh_expires_in and self._refresh_expires_in <= now
        ):
            self.getLoginToken()

    def reloadDevices(self):
        """load devices for each smart home"""
        if self._smartHomeData is not None:
            for y in range(len(self._smartHomeData)):
                zones = self.loadDevices(self._smartHomeData[y]["smarthome_id"])
                self._smartHomeData[y]["zones"] = zones

        return True

    def getSmartHomes(self):
        """Get smarthomes"""
        return self._smartHomeData

    def getDevice(self, smarthome: str, deviceId: str):
        """Get specific device"""
        for y in range(len(self._smartHomeData)):
            if self._smartHomeData[y]["smarthome_id"] == smarthome:
                for z in range(len(self._smartHomeData[y]["zones"])):
                    for x in range(len(self._smartHomeData[y]["zones"][z]["devices"])):
                        if self._smartHomeData[y]["zones"][z]["devices"][x]["id"] == deviceId:
                            return self._smartHomeData[y]["zones"][z]["devices"][x]

        return None

    def setDevice(self, smarthome: str, deviceId: str, newState: str):
        """Set specific device"""
        for y in range(len(self._smartHomeData)):
            if self._smartHomeData[y]["smarthome_id"] == smarthome:
                for z in range(len(self._smartHomeData[y]["zones"])):
                    for x in range(len(self._smartHomeData[y]["zones"][z]["devices"])):
                        if self._smartHomeData[y]["zones"][z]["devices"][x]["id"] == deviceId:
                            # If device is found, overwrite it with the new state
                            self._smartHomeData[y]["zones"][z]["devices"][x] = newState
                            return self._smartHomeData[y]["zones"][z]["devices"][x]

        return None

    def pushTemperature(
        self,
        smarthome: str,
        deviceID: str,
        value: str,
        gvMode: str,
        firstTry: bool = True,
    ):
        self._refresh_token_if_expired()

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "0",
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "peremption": "15000",
                "lang": "nl_NL",
            }
        extrapayload = {}
        if gvMode == "0":
            extrapayload = {
                "query[consigne_confort]": value,
                "query[consigne_manuel]": value,
            }
        elif gvMode == "1":
            extrapayload = {
                "query[consigne_manuel]": "0",
            }
        elif gvMode == "2":
            extrapayload = {
                "query[consigne_hg]": "446",
                "query[consigne_manuel]": "446",
                "peremption": "20000",
            }
        elif gvMode == "3":
            extrapayload = {
                "query[consigne_eco]": value,
                "query[consigne_manuel]": value,
            }
        elif gvMode == "4":
            extrapayload = {
                "query[time_boost]": "7200",
                "query[consigne_boost]": value,
                "query[consigne_manuel]": value,
            }
        elif gvMode == "11":
            extrapayload = {
                "query[consigne_manuel]": value,
            }
        payload.update(extrapayload)

        push_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/query/push/",
            headers=headers,
            data=payload,
        )

        if self.check_response(push_result):
            return True
        return False

    def getLastCommunication(self, smarthome: str, firstTry: bool = True):
        self._refresh_token_if_expired()

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {
            "token": "true",
            "smarthome_id": smarthome,
            "lang": "nl_NL"
        }

        last_connection_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/sandbox/check_last_connexion/",
            headers=headers,
            data=payload,
        )

        if self.check_response(last_connection_result):
            return last_connection_result.json()["data"]

        return None

    @staticmethod
    def check_response(response: requests.Response) -> bool:
        if response.status_code == 200:
            if "OK" in response.json()["code"]["key"]:
                return True
            else:
                # raise APIException("Code: {0}, key: {1}, value: {2}".format(
                #     response.json()["code"]["code"],
                #     response.json()["code"]["key"],
                #     response.json()["code"]["value"]
                # ))
                _LOGGER.error(
                    "Something went wrong fetching user data. Code: {}, Key: {}, Value: {}, Data: {}".format(
                        response.json()["code"]["code"],
                        response.json()["code"]["key"],
                        response.json()["code"]["value"],
                        response.json()["data"],
                    )
                )
                return False
        if response.status_code == 401:
            # raise UnauthorizedException("Unauthorized")
            _LOGGER.error("Unauthorized")
            return False
        else:
            # raise UnHandledStatuException(response.status_code)
            _LOGGER.error("Unhandled status code {}".format(response_status_code))
            return False
