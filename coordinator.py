"""DataUpdateCoordinator for our integration."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME, CONF_PIN,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .utils.parsers import parse_common_device_into_readable_obj
from .api import APIUnauthorizedError
from .managers.token_manager import GlobalTokenRepository
from .api import API, APIConnectionError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MainCoordinator(DataUpdateCoordinator):
    """The main coordinator"""

    data: list[dict[str, Any]]

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]
        self.pin = config_entry.data[CONF_PIN]

        # set variables from options
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialize DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here and make available to your integration.
        self.api = API(hass=hass, user=self.user, pwd=self.pwd, pin=self.pin)

    async def async_update_data(self):
        """Fetch data from API endpoint"""
        try:

            # If no token is saved, we execute a new login request before
            # calling the retrival of the devices statuses
            if GlobalTokenRepository.token is None:
                await self.hass.async_add_executor_job(self.api.execute_login)

            # Retrieve the devices statuses
            try:

                # Retrieve the new devices status from the API
                new_data_to_parse = await self.hass.async_add_executor_job(self.api.get_updated_devices_statuses)

                # For every retrieved device, we need to retrieve its details
                for device in new_data_to_parse:

                    # Retrieve the details of the current device
                    device_details = await self.hass.async_add_executor_job(self.api.get_device_details, device.serial, self.pin)

                    # We log the retrieved device's details
                    _LOGGER.debug(f"{device.serial} - DETAILS")
                    _LOGGER.debug(device_details.to_json())

                    # We set the device details inside the device DTO for future usage
                    device.details = device_details

                # Log the devices not parsed in a readable way for Home Assistant
                _LOGGER.debug("NEW DATA - NOT PARSED")
                _LOGGER.debug(new_data_to_parse)

                # Parse the data in a readable way for Home Assistant
                new_data_parsed = parse_common_device_into_readable_obj(new_data_to_parse)

                # Log the devices parsed in a readable way from Home Assistant
                _LOGGER.debug("NEW DATA - PARSED")
                _LOGGER.debug(new_data_parsed)

                # Set the new parsed data in the state
                data = new_data_parsed

            # API Unauthorized error handling
            #
            # In case of an API unauthorized error, it is likely a token expired / no more valid
            # issue. In order to be sure to have a valid / fresh token. We remove it and remake the request.
            # This will execute the same request, but before doing it, a new login request will be made
            except APIUnauthorizedError as err:
                _LOGGER.error(f"An authorization error occurred ({err}), removing the token to execute a new login in the next request")
                GlobalTokenRepository.token = None
                return await self.async_update_data()

            # Default error handling
            except Exception as err:
                _LOGGER.debug("Error on Login request: %s", err)
                raise UpdateFailed(err) from err

        except APIConnectionError as err:
            _LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return data

    def get_device(self, device_id: int) -> dict[str, Any]:
        """Get a device entity from our api data."""
        try:
            return [
                devices for devices in self.data if devices["device_id"] == device_id
            ][0]
        except (TypeError, IndexError):
            # In this case if the device id does not exist you will get an IndexError.
            # If api did not return any data, you will get TypeError.
            return None

    def get_device_parameter(self, device_id: int, parameter: str) -> Any:
        """Get the parameter value of one of our devices from our api data."""
        if device := self.get_device(device_id):
            return device.get(parameter)
