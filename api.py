import json
import logging
from typing import Any, Dict

import requests
from homeassistant.core import HomeAssistant

from .repositories.global_idp_repository import GlobalIdpRepository
from .models.common.common_device_details_model import CommonDeviceDetailsModel
from .models.requests.request_command_model import RequestCommandModel
from .models.common.common_plant_model import CommonPlantModel
from .models.responses.response_common_wrapper import ResponseCommonResponseWrapper
from .models.common.common_device_model import CommonDeviceModel
from .const import CYPHER_DEVICE_ID, PUSH_NOTIFICATION_PLATFORM, PUSH_NOTIFICATION_TOKEN, API_LOGIN_URL, \
    API_LOGIN_HEADERS, GET_DEVICES_HEADERS, API_GET_PLANTS_URL, API_SEND_PICO_CMD, API_GET_PICO_DETAILS, \
    EXECUTE_COMMANDS_HEADERS
from .managers.api_key_manager import retrieve_api_key
from .managers.token_manager import TokenManager, GlobalTokenRepository
from .models.requests.request_login_model import RequestLoginModel
from .models.responses.response_user_model import ResponseUserModel

_LOGGER = logging.getLogger(__name__)

tokenManager = TokenManager(ref="MainTokenManager")

class API:
    """Class for example API."""

    def __init__(self, hass: HomeAssistant, user: str, pwd: str, pin: str) -> None:
        """Initialise."""
        self.hass = hass
        self.user = user
        self.pwd = pwd
        self.pin = pin

    # Function to execute the login, it returns the user model
    def execute_login(self) -> ResponseUserModel:
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

            return response_parsed

        # Timeout error handling
        except requests.exceptions.ConnectTimeout as err:
            _LOGGER.error("Timeout connecting to api", err)
            raise APIConnectionError("Timeout connecting to api") from err

        # Default error handling
        except Exception as e:
            _LOGGER.debug("Error on Login request: %s", e)
            raise APIConnectionError("Exception on Login request") from e

    # Function to get the list of the devices of the user
    def get_updated_devices_statuses(self) -> list[CommonDeviceModel]:
        try:

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

            # Execute the request
            r = requests.get(API_GET_PLANTS_URL, headers=headers_to_use, timeout=10)

            # Log the response
            _LOGGER.debug("*** PLANTS RESPONSE ***")
            _LOGGER.debug(r.json())

            # If we retrieve a 401, we raise an APIUnauthorized error, that will be handled by the coordinator
            if r.status_code == 401:
                _LOGGER.debug("PLANTS RESPONSE Unauthorized!")
                raise APIUnauthorizedError()

            # Parse the response in the response DTO
            response_parsed = ResponseCommonResponseWrapper.from_json(r.json())

            # Parse the ResDescr field in JSON
            devices_list_json_to_parse = json.loads(response_parsed.res_descr)

            # Create a list of parsed devices based on the generated JSON list
            devices_parsed_list = []
            for plant in devices_list_json_to_parse:
                parsed_plant = CommonPlantModel.from_json(plant)
                for device in parsed_plant.devices:
                    devices_parsed_list.append(device)

            return devices_parsed_list

        # Timeout error handling
        except requests.exceptions.ConnectTimeout as err:
            _LOGGER.error("Timeout connecting to api", err)
            raise APIConnectionError("Timeout connecting to api") from err

        # Passing the exception to caller
        except APIUnauthorizedError as err:
            raise APIUnauthorizedError("Unauthorized") from err

        # Default error handling
        except Exception as err:
            _LOGGER.debug("Error on GetDevices request: %s", err)
            raise APIConnectionError("Exception on GetDevices request") from err

    # Function to execute a command on a specific device
    def execute_command(self, device_name: str, device_serial: str, device_pin: str, command_to_send: dict[str, str]):

        try:

            # Retrieve the new token to use
            token_to_use = tokenManager.retrieve_new_token()

            # Retrieve the email of the user
            email = self.user

            # Retrieve the new authorization to use
            authorization = retrieve_api_key(email)

            # Create the headers obj that will be used in the request
            headers_to_use = {
                **EXECUTE_COMMANDS_HEADERS,
                "Authorization": authorization,
                "Token": token_to_use
            }

            # Create the parameters obj that will be used in the request
            params_to_use = {
                "picoSerial": device_serial,
                "PIN": device_pin,
            }

            # Create the body obj that will be used in the request
            body_to_use = (RequestCommandModel(
                command=command_to_send,
                device_name=device_name,
                pin=device_pin,
                serial=device_serial
            ).to_json_string())

            # Log the response
            _LOGGER.debug("*** EXECUTE COMMANDS REQUEST HEADERS ***")
            _LOGGER.debug(headers_to_use)

            # Log the response
            _LOGGER.debug("*** EXECUTE COMMANDS REQUEST PARAMETERS ***")
            _LOGGER.debug(params_to_use)

            # Log the response
            _LOGGER.debug("*** EXECUTE COMMANDS REQUEST BODY ***")
            _LOGGER.debug(body_to_use)

            # Execute the request
            r = requests.post(API_SEND_PICO_CMD, headers=headers_to_use, params=params_to_use, data=body_to_use, timeout=10)

            # Increment the IDP counter
            GlobalIdpRepository.idpCounter += 1

            # Log the response
            _LOGGER.debug("*** EXECUTE COMMANDS RESPONSE ***")
            _LOGGER.debug(r.json())
            _LOGGER.debug(r.url)

        # Timeout error handling
        except requests.exceptions.ConnectTimeout as err:
            _LOGGER.error("Timeout connecting to api", err)
            raise APIConnectionError("Timeout connecting to api") from err

        # Passing the exception to caller
        except APIUnauthorizedError as err:
            raise APIUnauthorizedError("Unauthorized") from err

        # Default error handling
        except Exception as err:
            _LOGGER.debug("Error on ExecuteCommands request: %s", err)
            raise APIConnectionError("Exception on ExecuteCommands request") from err

    # Function to retrieve the details of a specific device
    def get_device_details(self, device_serial: str, device_pin: str) -> CommonDeviceDetailsModel:
        try:

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

            # Create the parameters obj that will be used in the request
            params_to_use = {
                "picoSerial": device_serial,
                "PIN": device_pin,
            }

            # Log the request
            _LOGGER.debug("*** GET PICO DETAILS HEADERS ***")
            _LOGGER.debug(headers_to_use)

            # Log the request
            _LOGGER.debug("*** GET PICO DETAILS PARAMETERS ***")
            _LOGGER.debug(params_to_use)

            # Execute the request
            r = requests.get(API_GET_PICO_DETAILS, headers=headers_to_use, params=params_to_use, timeout=10)

            # Log the response
            _LOGGER.debug("*** GET PICO DETAILS RESPONSE ***")
            _LOGGER.debug(r.json())

            # Parse the response in the response DTO
            response_parsed = ResponseCommonResponseWrapper.from_json(r.json())

            # Parse the ResDescr field in JSON
            obj_to_parse = json.loads(response_parsed.res_descr)
            obj_to_parse["Serial"] = device_serial

            device_details_model = CommonDeviceDetailsModel.from_json(obj_to_parse)

            return device_details_model

        # Timeout error handling
        except requests.exceptions.ConnectTimeout as err:
            _LOGGER.error("Timeout connecting to api", err)
            raise APIConnectionError("Timeout connecting to api") from err

        # Passing the exception to caller
        except APIUnauthorizedError as err:
            raise APIUnauthorizedError("Unauthorized") from err

        # Default error handling
        except Exception as err:
            _LOGGER.debug("Error on GetDeviceDetails request: %s", err)
            raise APIConnectionError("Exception on GetDeviceDetails request") from err

class APIAuthError(Exception):
    """Exception class for auth error."""

class APIConnectionError(Exception):
    """Exception class for connection error."""

class APIUnauthorizedError(Exception):
    """Exception class for unauthorized error."""
