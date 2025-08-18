"""Base entity which all other entity platform classes can inherit."""

import logging
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MainCoordinator

_LOGGER = logging.getLogger(__name__)


class BaseEntity(CoordinatorEntity):
    """Base Entity Class.

    This inherits a CoordinatorEntity class to register your entites to be updated
    by your DataUpdateCoordinator when async_update_data is called, either on the scheduled
    interval or by forcing an update.
    """

    coordinator: MainCoordinator

    # ----------------------------------------------------------------------------
    # Using attr_has_entity_name = True causes HA to name your entities with the
    # device name and entity name.  Ie if your name property of your entity is
    # Voltage and this entity belongs to a device, Lounge Socket, this will name
    # your entity to be sensor.lounge_socket_voltage
    # ----------------------------------------------------------------------------
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: MainCoordinator, device: dict[str, Any], parameter: str
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device["device_id"]
        self.parameter = parameter

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device(self.device_id)
        _LOGGER.debug(
            "Updating device: %s, %s",
            self.device_id,
            self.coordinator.get_device_parameter(self.device_id, "device_name"),
        )
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        # ----------------------------------------------------------------------------
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the identifiers
        # parameter to link an entity to a device.
        # If your device connects via another device, add via_device parameter with
        # the identifiers of that device.
        #
        # Device identifiers should be unique, so use your integration name (DOMAIN)
        # and a device uuid, mac address or some other unique attribute.
        # ----------------------------------------------------------------------------
        return DeviceInfo(
            name=self.coordinator.get_device_parameter(self.device_id, "device_name"),
            manufacturer="Tecnosystemi",
            model=str(
                self.coordinator.get_device_parameter(self.device_id, "device_type")
            )
            .replace("_", " ")
            .title(),
            sw_version=self.coordinator.get_device_parameter(
                self.device_id, "software_version"
            ),
            identifiers={
                (
                    DOMAIN,
                    self.coordinator.get_device_parameter(self.device_id, "device_uid"),
                )
            },
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.parameter.replace("_", " ").title()

    @property
    def unique_id(self) -> str:
        """Return unique id."""

        # ----------------------------------------------------------------------------
        # All entities must have a unique id across your whole Home Assistant server -
        # and that also goes for anyone using your integration who may have many other
        # integrations loaded.
        #
        # Think carefully what you want this to be as changing it later will cause HA
        # to create new entities.
        #
        # It is recommended to have your integration name (DOMAIN), some unique id
        # from your device such as a UUID, MAC address etc (not IP address) and then
        # something unique to your entity (like name - as this would be unique on a
        # device)
        #
        # If in your situation you have some hub that connects to devices which then
        # you want to create multiple sensors for each device, you would do something
        # like.
        #
        # f"{DOMAIN}-{HUB_MAC_ADDRESS}-{DEVICE_UID}-{ENTITY_NAME}""
        #
        # This is even more important if your integration supports multiple instances.
        # ----------------------------------------------------------------------------
        return f"{DOMAIN}-{self.coordinator.get_device_parameter(self.device_id, "device_uid")}-{self.parameter}"
