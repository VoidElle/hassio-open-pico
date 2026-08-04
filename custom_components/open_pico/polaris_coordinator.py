"""DataUpdateCoordinator for Polaris 5X devices (local TCP port 1235)."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from open_polaris_local_api import PolarisLocalClient, PolarisApiError, PolarisDevice, PolarisZone

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Local TCP polling (port 1235).
# 30 seconds avoids overwhelming the CU's limited TCP stack,
# which would block the official app's cloud sync.
POLARIS_SCAN_INTERVAL = 30

@dataclass
class PolarisData:
    """Container for Polaris coordinator data."""

    device: PolarisDevice
    zones: list[PolarisZone]


class PolarisCoordinator(DataUpdateCoordinator[PolarisData]):
    """Coordinator for a single Polaris CU (Control Unit) via local TCP."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: PolarisLocalClient,
        device_name: str,
        scan_interval: int = POLARIS_SCAN_INTERVAL,
    ) -> None:
        """Initialize."""
        self.client = client
        self.device_name = device_name
        self.polaris_ip = client.ip
        self._zone_details: dict[int, dict] = {}
        self._zone_details_fetched = False

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} Polaris ({device_name})",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=scan_interval),
        )

    @property
    def serial(self) -> str:
        """Return device serial (from last status, or IP-based fallback)."""
        if self.client.device and self.client.device.serial:
            return self.client.device.serial
        return self.client.ip.replace(".", "_")

    async def _async_update_data(self) -> PolarisData:
        """Fetch device + zone data via local TCP."""
        try:
            device, zones = await self.client.async_update()

            # Fetch zone details (serranda/fancoil) on first successful update.
            # stato_zona returns per-zone data not included in stato_r.
            # Skips offline zones and uses a 10s timeout to avoid blocking setup.
            if not self._zone_details_fetched and zones:
                try:
                    async with asyncio.timeout(10):
                        self._zone_details = await self.client.fetch_all_zone_details()
                    self._zone_details_fetched = True
                    _LOGGER.info(
                        "[%s] Fetched zone details for %d zones",
                        self.device_name, len(self._zone_details),
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "[%s] Failed to fetch zone details: %s",
                        self.device_name, err,
                    )
                    self._zone_details_fetched = True  # don't retry every poll

            # Merge cached serranda/fancoil data into zones
            # (stato_r doesn't include these fields)
            for z in zones:
                detail = self._zone_details.get(z.zone_id)
                if detail:
                    z.serranda = detail.get("shu", -1)
                    z.serranda_set = detail.get("shu_set", -1)
                    z.fancoil = detail.get("fan", -1)
                    z.fancoil_set = detail.get("fan_set", -1)

            _LOGGER.debug(
                "[%s] Polaris update: on=%s, mode=%s, zones=%d",
                self.device_name,
                device.is_on,
                device.cooling_mode_name,
                len(zones),
            )

            if self.client.verbose:
                _LOGGER.debug(
                    "[Polaris][%s] Device state: is_off=%s, is_cooling=%s, "
                    "operating_mode=%d (%s), t_can=%s, f_inv=%s, f_est=%s, "
                    "ir_present=%s, num_errors=%s, serial=%s, fw=%s",
                    self.device_name,
                    device.is_off, device.is_cooling,
                    device.operating_mode, device.cooling_mode_name,
                    device.t_can, device.f_inv, device.f_est,
                    device.ir_present, device.num_errors,
                    device.serial, device.fw_ver,
                )
                for z in zones:
                    _LOGGER.debug(
                        "[Polaris][%s] Zone '%s' (id=%d): is_off=%s, "
                        "temp=%s, set_temp=%s, humidity=%s, set_humidity=%s, "
                        "fancoil=%s, fancoil_set=%s, serranda=%s, serranda_set=%s, "
                        "ev=%s, is_crono=%s, num_error=%s",
                        self.device_name, z.name, z.zone_id,
                        z.is_off, z.current_temp, z.set_temp,
                        z.humidity, z.set_humidity,
                        z.fancoil, z.fancoil_set,
                        z.serranda, z.serranda_set,
                        z.ev, z.is_crono_mode, z.num_error,
                    )

            return PolarisData(device=device, zones=zones)

        except PolarisApiError as err:
            raise UpdateFailed(f"Polaris error: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Polaris timeout: {err}") from err
        except Exception as err:
            _LOGGER.error(
                "[%s] Error polling Polaris: %s",
                self.device_name, err, exc_info=True,
            )
            raise UpdateFailed(f"Error polling Polaris: {err}") from err

    # ─── Helper properties ───────────────────────────────────────────

    @property
    def polaris_device(self) -> PolarisDevice | None:
        return self.data.device if self.data else None

    @property
    def polaris_zones(self) -> list[PolarisZone]:
        return self.data.zones if self.data else []

    # ─── Control methods: device-level ───────────────────────────────

    async def async_turn_on(self) -> None:
        """Turn device on."""
        await self.client.turn_on()
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn device off."""
        await self.client.turn_off()
        await self.async_request_refresh()

    async def async_set_cooling_mode(self, mode: int) -> None:
        """Set cooling mode (1=raff, 2=deum, 3=vent)."""
        await self.client.set_cooling_mode(mode)
        await self.async_request_refresh()

    async def async_set_heating_mode(self) -> None:
        """Switch to heating mode."""
        await self.client.set_heating_mode()
        await self.async_request_refresh()

    # ─── Control methods: zone-level ─────────────────────────────────

    def _find_zone(self, zone_id: int) -> PolarisZone | None:
        """Find zone by ID in current data."""
        for z in self.polaris_zones:
            if z.zone_id == zone_id:
                return z
        return None

    async def async_set_zone_temp(self, zone_id: int, temperature: float) -> None:
        """Set zone target temperature."""
        zone = self._find_zone(zone_id)
        if zone:
            await self.client.set_zone_temp(zone, temperature)
            await self.async_request_refresh()
        else:
            _LOGGER.error("Zone %d not found", zone_id)

    async def async_turn_zone_on(self, zone_id: int) -> None:
        """Turn a zone on."""
        zone = self._find_zone(zone_id)
        if zone:
            await self.client.turn_zone_on(zone)
            await self.async_request_refresh()

    async def async_turn_zone_off(self, zone_id: int) -> None:
        """Turn a zone off."""
        zone = self._find_zone(zone_id)
        if zone:
            await self.client.turn_zone_off(zone)
            await self.async_request_refresh()

    async def async_update_zone(self, zone_id: int, **kwargs) -> None:
        """Generic zone update with arbitrary kwargs."""
        zone = self._find_zone(zone_id)
        if zone:
            await self.client.update_zone(zone, **kwargs)
            await self.async_request_refresh()

    async def async_set_zone_serranda(self, zone_id: int, value: int) -> None:
        """Set serranda (damper) value for a zone.

        Args:
            zone_id: The zone to update.
            value: 0=Auto, 1=A1, 2=A2, 3=A3.

        Important: upd_zona requires fan_set and shu_set to be set to the
        same value. Sending fan_set=-1 causes the Polaris CU to hang.
        """
        zone = self._find_zone(zone_id)
        if zone:
            await self.client.set_zone_serranda(zone, value)
            # Update local cache so UI reflects the change immediately
            if zone_id in self._zone_details:
                self._zone_details[zone_id]["shu_set"] = value
                self._zone_details[zone_id]["shu"] = value
            await asyncio.sleep(2)  # let the CU process before polling
            await self.async_request_refresh()
        else:
            _LOGGER.error("Zone %d not found for serranda update", zone_id)

    @property
    def zone_details(self) -> dict[int, dict]:
        """Return cached zone details (from stato_zona)."""
        return self._zone_details

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and disconnect client."""
        await self.client.close()
