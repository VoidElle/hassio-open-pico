"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from copy import deepcopy
import logging
from typing import Any

import requests

from .const import CYPHER_DEVICE_ID, PUSH_NOTIFICATION_PLATFORM, PUSH_NOTIFICATION_TOKEN, BASE_URL, API_LOGIN_URL, \
    API_LOGIN_HEADERS
from .managers.api_key_manager import retrieve_api_key
from .managers.token_manager import TokenManager
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


class API:
    """Class for example API."""

    def __init__(self, user: str, pwd: str, mock: bool = False) -> None:
        """Initialise."""
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

            # Log the request
            _LOGGER.debug("*** LOGIN REQUEST ***")
            _LOGGER.debug(login_request.to_json())

            # Execute the request
            r = requests.post(API_LOGIN_URL, headers=headers_to_use, json=login_request.to_json(), timeout=10)

            # Log the response not parsed
            _LOGGER.debug("*** LOGIN RESPONSE NOT PARSED ***")
            _LOGGER.debug(r.json())

            # Parse the response in the DTO
            response_parsed = ResponseUserModel.from_json(r.json())

            # Log the response parsed
            _LOGGER.debug("*** LOGIN RESPONSE PARSED ***")
            _LOGGER.debug(response_parsed.to_json())

            return response_parsed

        except Exception as e:
            _LOGGER.debug("Error on Login request: %s", e)
            raise APIConnectionError("Exception on Login request") from e

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
