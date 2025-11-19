"""Open Pico integration for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import MainCoordinator
from .pico_manager import PicoClientManager

_LOGGER = logging.getLogger(__name__)

# The list of supported platforms
PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.SWITCH,
    Platform.SELECT,
]

# Define the device schema
DEVICE_SCHEMA = vol.Schema({
    vol.Required("ip"): cv.string,
    vol.Required("pin"): cv.string,
})

# Define your YAML configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required("devices"): vol.All(cv.ensure_list, [DEVICE_SCHEMA]),
        })
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Open Pico integration from YAML configuration."""

    # Check if domain is in config
    if DOMAIN not in config:
        return True

    # Get your domain's configuration from configuration.yaml
    domain_config = config[DOMAIN]
    devices = domain_config.get("devices", [])

    _LOGGER.info("Setting up %s with %d device(s)", DOMAIN, len(devices))

    # Initialize hass.data for this domain
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinators"] = []
    hass.data[DOMAIN]["config"] = domain_config

    # Create shared PicoClient manager
    manager = PicoClientManager()
    hass.data[DOMAIN]["manager"] = manager

    # Add all devices to manager and create coordinators
    for device in devices:
        pico_ip = device.get("ip")
        pin = device.get("pin")

        _LOGGER.debug("Setting up device: ip=%s, pin=%s", pico_ip, pin)

        try:
            # Add device to manager
            await manager.add_device(pico_ip, pin)

            # Initialize the coordinator for this device
            coordinator = MainCoordinator(hass, pico_ip, pin, manager)

            # Perform initial data load with timeout
            async with asyncio.timeout(30):
                await coordinator.async_refresh()

            # Check if we got data
            if not coordinator.data:
                _LOGGER.error("Failed to fetch initial data from device %s", pico_ip)
                continue

            # Store coordinator in our list
            hass.data[DOMAIN]["coordinators"].append(coordinator)
            _LOGGER.info("Successfully connected to device %s", pico_ip)

        except asyncio.TimeoutError:
            _LOGGER.error(
                "Timeout connecting to device %s. Check if device is reachable and PIN is correct.",
                pico_ip
            )
            continue
        except Exception as err:
            _LOGGER.error("Error setting up device %s: %s", pico_ip, err)
            continue

    # Check if we have at least one successful coordinator
    if not hass.data[DOMAIN]["coordinators"]:
        _LOGGER.error("No devices were successfully set up")
        await manager.shutdown()
        return False

    # Load platforms using discovery
    for platform in PLATFORMS:
        hass.async_create_task(
            discovery.async_load_platform(
                hass, platform, DOMAIN, {}, config
            )
        )

    _LOGGER.info("Successfully set up %s with %d device(s)",
                 DOMAIN, len(hass.data[DOMAIN]["coordinators"]))

    return True


async def async_unload_entry(hass: HomeAssistant) -> bool:
    """Unload the integration."""

    # Shutdown the shared manager
    if DOMAIN in hass.data and "manager" in hass.data[DOMAIN]:
        await hass.data[DOMAIN]["manager"].shutdown()

    # Remove services if you have any
    for service in hass.services.async_services_for_domain(DOMAIN):
        hass.services.async_remove(DOMAIN, service)

    # Clean up hass.data
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)

    return True