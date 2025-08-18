"""Config flows"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME, CONF_PIN,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .api import API, APIAuthError, APIConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Adjust the data schema to the data that you need
# ----------------------------------------------------------------------------
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME, description={"suggested_value": "email@email.com"}): str,
        vol.Required(CONF_PASSWORD, description={"suggested_value": "password"}): str,
        vol.Required(CONF_PIN, description={"suggested_value": "PIN"}): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        # ----------------------------------------------------------------------------
        # If your api is not async, use the executor to access it
        # If you cannot connect, raise CannotConnect
        # If the authentication is wrong, raise InvalidAuth
        # ----------------------------------------------------------------------------
        api = API(hass, data[CONF_USERNAME], data[CONF_PASSWORD], data[CONF_PIN])
        # await hass.async_add_executor_job(api.get_data)
        await hass.async_add_executor_job(api.execute_login)
    except APIAuthError as err:
        raise InvalidAuth from err
    except APIConnectionError as err:
        raise CannotConnect from err
    return {"title": f"Tecnosystemi API - {data[CONF_USERNAME]}"}


async def validate_settings(hass: HomeAssistant, data: dict[str, Any]) -> bool:
    """Another validation method for our config steps."""
    return True


class ExampleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Example Integration."""

    VERSION = 1
    _input_data: dict[str, Any]
    _title: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step.

        Called when you initiate adding an integration via the UI
        """

        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            try:
                # ----------------------------------------------------------------------------
                # Validate that the setup data is valid and if not handle errors.
                # You can do any validation you want or no validation on each step.
                # The errors["base"] values match the values in your strings.json and translation files.
                # ----------------------------------------------------------------------------
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Validation was successful, so proceed to the next step.

                # ----------------------------------------------------------------------------
                # Setting our unique id here just because we have the info at this stage to do that
                # and it will abort early on in the process if alreay setup.
                # You can put this in any step however.
                # ----------------------------------------------------------------------------
                await self.async_set_unique_id(info.get("title"))
                self._abort_if_unique_id_configured()

                # Set our title variable here for use later
                self._title = info["title"]

                # ----------------------------------------------------------------------------
                # You need to save the input data to a class variable as you go through each step
                # to ensure it is accessible across all steps.
                # ----------------------------------------------------------------------------
                self._input_data = user_input

                # Call the next step
                return self.async_create_entry(title=self._title, data=self._input_data)

        # Show initial form.
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            last_step=False,  # Adding last_step True/False decides whether form shows Next or Submit buttons
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add reconfigure step to allow to reconfigure a config entry.

        This methid displays a reconfigure option in the integration and is
        different to options.
        It can be used to reconfigure any of the data submitted when first installed.
        This is optional and can be removed if you do not want to allow reconfiguration.
        """
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            try:
                user_input[CONF_HOST] = "1.1.1.1"
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    unique_id=config_entry.unique_id,
                    data={**config_entry.data, **user_input},
                    reason="reconfigure_successful",
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=config_entry.data[CONF_USERNAME]
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_PIN): str,
                }
            ),
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
