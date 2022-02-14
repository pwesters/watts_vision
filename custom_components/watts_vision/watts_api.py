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
        self._refresh_token = None
        self._smartHomeData = {}

    def test_authentication(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            token = self.getLoginToken()
            return token is not None
        except Exception as exception:
            _LOGGER.exception("Authentication exception " + exception)
            return False

    def getLoginToken(self):
        """Get the login token for the Watts Smarthome API"""

        payload = {
            "grant_type": "password",
            "username": self._username,
            "password": self._password,
            "client_id": "app-front",
        }

        _LOGGER.debug("Trying to get an access token.")
        request_token_result = request_token_result = requests.post(
            url="https://smarthome.wattselectronics.com/auth/realms/watts/protocol/openid-connect/token",
            data=payload,
        )

        if request_token_result.status_code == 200:
            _LOGGER.debug("Requesting access token successful")
            token = request_token_result.json()["access_token"]
            self._token = token
            # Refresh token doesn't seem to bo useful because of
            # session
            self._refresh_token = request_token_result.json()["refresh_token"]
            return token
        else:
            _LOGGER.error(
                "Something went wrong fetching token: {}".format(
                    request_token_result.status_code
                )
            )
            raise None

    def loadData(self):
        """load data from api"""
        smarthomes = self.loadSmartHomes()
        self._smartHomeData = smarthomes

        """load devices for each smart home"""
        if self._smartHomeData is not None:
            for y in range(len(self._smartHomeData)):
                devices = self.loadDevices(self._smartHomeData[str(y)]["smarthome_id"])
                self._smartHomeData[str(y)]["devices"] = devices

        return True

    def loadSmartHomes(self, firstTry: bool = True):
        """Load the user data"""
        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {"token": "true", "email": self._username, "lang": "nl_NL"}

        user_data_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/user/read/",
            headers=headers,
            data=payload,
        )

        if user_data_result.status_code == 200:
            if (
                user_data_result.json()["code"]["code"] == "1"
                and user_data_result.json()["code"]["key"] == "OK"
                and user_data_result.json()["code"]["value"] == "OK"
            ):
                return user_data_result.json()["data"]["smarthomes"]
            else:
                if firstTry:
                    # Token may be expired, try to fetch new token
                    self.getLoginToken()
                    return self.loadSmartHomes(firstTry=False)
                else:
                    _LOGGER.error(
                        "Something went wrong fetching user data. Code: {}, Key: {}, Value: {}, Data: {}".format(
                            user_data_result.json()["code"]["code"],
                            user_data_result.json()["code"]["key"],
                            user_data_result.json()["code"]["value"],
                            user_data_result.json()["data"],
                        )
                    )
                    return None
        else:
            _LOGGER.error(
                "Something went wrong fetching user data: {}".format(
                    user_data_result.status_code
                )
            )
            return None

    def loadDevices(self, smarthome: str, firstTry: bool = True):
        """Load devices for smart home"""

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {"token": "true", "smarthome_id": smarthome, "lang": "nl_NL"}

        devices_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/smarthome/read",
            headers=headers,
            data=payload,
        )

        if devices_result.status_code == 200:
            if (
                devices_result.json()["code"]["code"] == "1"
                and devices_result.json()["code"]["key"] == "OK"
                and devices_result.json()["code"]["value"] == "OK"
            ):
                return devices_result.json()["data"]["devices"]
            else:
                if firstTry:
                    # Token may be expired, try to fetch new token
                    self.getLoginToken()
                    return self.loadDevices(smarthome, firstTry=False)
                else:
                    _LOGGER.error(
                        "Something went wrong fetching user data. Code: {}, Key: {}, Value: {}, Data: {}".format(
                            devices_result.json()["code"]["code"],
                            devices_result.json()["code"]["key"],
                            devices_result.json()["code"]["value"],
                            devices_result.json()["data"],
                        )
                    )
                    return None
        else:
            _LOGGER.error(
                "Something went wrong fetching devices: {}".format(
                    devices_result.status_code
                )
            )
            return None

    def reloadDevices(self):
        """load devices for each smart home"""
        if self._smartHomeData is not None:
            for y in range(len(self._smartHomeData)):
                devices = self.loadDevices(self._smartHomeData[str(y)]["smarthome_id"])
                self._smartHomeData[str(y)]["devices"] = devices

        return True

    def getSmartHomes(self):
        """Get smarthomes"""
        return self._smartHomeData

    def getDevice(self, smarthome: str, deviceId: str):
        """Get specific device"""
        for y in range(len(self._smartHomeData)):
            if self._smartHomeData[str(y)]["smarthome_id"] == smarthome:
                for x in range(len(self._smartHomeData[str(y)]["devices"])):
                    if self._smartHomeData[str(y)]["devices"][str(x)]["id"] == deviceId:
                        return self._smartHomeData[str(y)]["devices"][str(x)]

        return None

    def pushTemperature(
        self,
        smarthome: str,
        deviceID: str,
        value: str,
        gvMode: str,
        firstTry: bool = True,
    ):
        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {}
        if gvMode == "0":
            payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "0",
                "query[consigne_confort]": value,
                "query[consigne_manuel]": value,
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "peremption": "15000",
                "lang": "nl_NL",
            }
        if gvMode == "1":
            payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "0",
                "query[consigne_manuel]": "0",
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "peremption": "15000",
                "lang": "nl_NL",
            }
        if gvMode == "2":
            payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "0",
                "query[consigne_hg]": "446",
                "query[consigne_manuel]": "446",
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "peremption": "20000",
                "lang": "nl_NL",
            }
        if gvMode == "3":
            payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "0",
                "query[consigne_eco]": value,
                "query[consigne_manuel]": value,
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "peremption": "15000",
                "lang": "nl_NL",
            }
        if gvMode == "4":
            payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "7200",
                "query[consigne_boost]": value,
                "query[consigne_manuel]": value,
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "peremption": "15000",
                "lang": "nl_NL",
            }
        if gvMode == "11":
            payload = {
                "token": "true",
                "context": "1",
                "smarthome_id": smarthome,
                "query[id_device]": deviceID,
                "query[time_boost]": "0",
                "query[gv_mode]": gvMode,
                "query[nv_mode]": gvMode,
                "query[consigne_manuel]": value,
                "peremption": "15000",
                "lang": "nl_NL",
            }

        push_result = requests.post(
            url="https://smarthome.wattselectronics.com/api/v0.1/human/query/push/",
            headers=headers,
            data=payload,
        )

        if push_result.status_code == 200:
            if (
                push_result.json()["code"]["key"] == "OK_SET"
                and push_result.json()["code"]["value"] == "Insert / update success"
            ):
                return True
            else:
                if firstTry:
                    # Token may be expired, try to fetch new token
                    self.getLoginToken()
                    return self.pushTemperature(
                        smarthome, deviceID, value, gvMode, firstTry=False
                    )
                else:
                    _LOGGER.error(
                        "Something went wrong updating the device. Code: {}, Key: {}, Value: {}, Data: {}".format(
                            push_result.json()["code"]["code"],
                            push_result.json()["code"]["key"],
                            push_result.json()["code"]["value"],
                            push_result.json()["data"],
                        )
                    )
                    return False
        else:
            _LOGGER.error(
                "Something went wrong updating the device: {}".format(
                    push_result.status_code
                )
            )
            return False

    def getLastCommunication(self, smarthome: str, firstTry: bool = True):
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

        if last_connection_result.status_code == 200:
            if (
                last_connection_result.json()["code"]["code"] == "1"
                and last_connection_result.json()["code"]["key"] == "OK"
                and last_connection_result.json()["code"]["value"] == "OK"
            ):
                return last_connection_result.json()["data"]
            else:
                if firstTry:
                    # Token may be expired, try to fetch new token
                    self.getLoginToken()
                    return self.getLastCommunication(smarthome, firstTry=False)
                else:
                    _LOGGER.error(
                        "Something went wrong fetching user data. Code: {}, Key: {}, Value: {}, Data: {}".format(
                            last_connection_result.json()["code"]["code"],
                            last_connection_result.json()["code"]["key"],
                            last_connection_result.json()["code"]["value"],
                            last_connection_result.json()["data"],
                        )
                    )
                    return None
        else:
            _LOGGER.error(
                "Something went wrong fetching devices: {}".format(
                    last_connection_result.status_code
                )
            )
            return None
