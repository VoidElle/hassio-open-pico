"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from copy import deepcopy
import logging
from typing import Any, Dict

import requests
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CYPHER_DEVICE_ID, PUSH_NOTIFICATION_PLATFORM, PUSH_NOTIFICATION_TOKEN, BASE_URL, API_LOGIN_URL, \
    API_LOGIN_HEADERS, GET_DEVICES_HEADERS, API_GET_PLANTS_URL
from .managers.api_key_manager import retrieve_api_key
from .managers.token_manager import TokenManager, GlobalTokenRepository
from .models.common.common_plant_model import CommonPlantModel
from .models.requests.request_login_model import RequestLoginModel
from .models.responses.response_user_model import ResponseUserModel

_LOGGER = logging.getLogger(__name__)

tokenManager = TokenManager(ref="MainTokenManager")

MOCK_DATA = [
    {
        "device_id": 1,
        "device_type": "FAN",
        "device_name": "Lounge Fan",
        "device_uid": "0123-4599-1541-1793",
        "software_version": "2.11",
        "state": "ON",
        "oscillating": "OFF",
        "speed": 2,
    },
]

DEVICES_LIST = []

class API:
    """Class for example API."""

    def __init__(self, hass: HomeAssistant, user: str, pwd: str, mock: bool = False) -> None:
        """Initialise."""
        self.hass = hass
        self.host = "1.1.1.1"
        self.user = user
        self.pwd = pwd

        # For getting and setting the mock data
        self.mock = mock
        self.mock_data = deepcopy(MOCK_DATA)

        # Mock auth error if user != test and pwd != 1234
        # if mock and (self.user != "test" or self.pwd != "1234"):
            # raise APIAuthError("Invalid credentials!")

    def execute_login(self):
        """Execute login."""
        try:

            # Encrypt the password using the TokenManager class
            password = tokenManager.encrypt_text(self.pwd)

            # Create the request model, and we log it for debug purposes
            login_request = RequestLoginModel(CYPHER_DEVICE_ID, PUSH_NOTIFICATION_PLATFORM, password, PUSH_NOTIFICATION_TOKEN, self.user)
            _LOGGER.debug(login_request.to_json())

            # Retrieve the authorization that needs to use in the headers
            authorization = retrieve_api_key(None)

            # Create the headers obj that will be used in the request
            headers_to_use = {
                **API_LOGIN_HEADERS,
                "Authorization": authorization
            }

            # Parse the body to json
            json_request: Dict[str, Any] = login_request.to_json()

            # Log the request
            _LOGGER.debug("*** LOGIN REQUEST ***")
            _LOGGER.debug(json_request)

            # Execute the request
            r = requests.post(API_LOGIN_URL, headers=headers_to_use, json=json_request, timeout=10)

            # Log the response not parsed
            _LOGGER.debug("*** LOGIN RESPONSE NOT PARSED ***")
            _LOGGER.debug(r.json())

            # Parse the response in the DTO
            response_parsed = ResponseUserModel.from_json(r.json())

            # Set the response's user token as the initial token
            GlobalTokenRepository.token = response_parsed.token

            # Log the response parsed
            _LOGGER.debug("*** LOGIN RESPONSE PARSED ***")
            _LOGGER.debug(response_parsed.to_json())

            # Clear the devices list to avoid duplicates
            DEVICES_LIST.clear()

            # For every device in the user's devices list
            # We append it into the devices list
            for plant in response_parsed.plants:
                for device in plant.devices:
                    DEVICES_LIST.append({
                        "device_id": device.id,
                        "device_type": "FAN",
                        "device_name": device.name,
                        "device_uid": device.serial,
                        "software_version": "2.11",
                        "state": "OFF" if device.is_off else "ON",
                    })

            return response_parsed

        except Exception as e:
            _LOGGER.debug("Error on Login request: %s", e)
            raise APIConnectionError("Exception on Login request") from e

    async def get_updated_devices_statuses(self) -> list[CommonPlantModel]:

        # Retrieve the new token to use
        token_to_use = tokenManager.retrieve_new_token()

        # Retrieve the email of the user
        email = self.user

        # Retrieve the new authorization to use
        authorization = retrieve_api_key(email)

        # Create the headers obj that will be used in the request
        headers_to_use = {
            **GET_DEVICES_HEADERS,
            "Authorization": authorization,
            "Token": token_to_use
        }

        # Log the response
        _LOGGER.debug("*** PLANTS REQUEST HEADERS ***")
        _LOGGER.debug(headers_to_use)

        # Execute the request in a non-blocking way
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(API_GET_PLANTS_URL, headers=headers_to_use) as resp:
                _LOGGER.debug("*** PLANTS RESPONSE ***")
                _LOGGER.debug(resp)
                return []
        except requests.exceptions.ConnectTimeout as err:
            _LOGGER.error("Timeout connecting to api", err)
            raise APIConnectionError("Timeout connecting to api") from err
        except Exception as err:
            _LOGGER.error(err)

        return []

    def get_data(self) -> list[dict[str, Any]]:
        """Get api data."""
        if self.mock:
            return self.get_mock_data()
        try:
            r = requests.get(f"http://{self.host}/api", timeout=10)
            return r.json()
        except requests.exceptions.ConnectTimeout as err:
            raise APIConnectionError("Timeout connecting to api") from err

    def set_data(self, device_id: int, parameter: str, value: Any) -> bool:
        """Set api data."""
        if self.mock:
            return self.set_mock_data(device_id, parameter, value)
        try:
            data = {parameter, value}
            r = requests.post(
                f"http://{self.host}/api/{device_id}", json=data, timeout=10
            )
        except requests.exceptions.ConnectTimeout as err:
            raise APIConnectionError("Timeout connecting to api") from err
        else:
            return r.status_code == 200

    # ----------------------------------------------------------------------------
    # The below methods are used to mimic a real api for the example that changes
    # its values based on commands from the switches and lights and obvioulsy will
    # not be needed wiht your real api.
    # ----------------------------------------------------------------------------
    def get_mock_data(self) -> dict[str, Any]:
        """Get mock api data."""
        return self.mock_data

    def set_mock_data(self, device_id: int, parameter: str, value: Any) -> bool:
        """Update mock data."""
        try:
            device = [
                devices
                for devices in self.mock_data
                if devices.get("device_id") == device_id
            ][0]
        except IndexError:
            # Device id does not exist
            return False

        other_devices = [
            devices
            for devices in self.mock_data
            if devices.get("device_id") != device_id
        ]

        # Modify device parameter
        if device.get(parameter):
            device[parameter] = value
        else:
            # Parameter does not exist on device
            return False

        _LOGGER.debug("Device Updated: %s", device)

        # Update mock data
        self.mock_data = other_devices
        self.mock_data.append(device)
        return True


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
