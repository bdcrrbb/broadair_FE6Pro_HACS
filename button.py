"""Button platform for Broad Fresh Air."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import BroadAirCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Broad Fresh Air button entities from config entry."""
    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        BroadAirResetHEPAFilterButton(coordinator, entry),
        BroadAirResetCoarseFilterButton(coordinator, entry),
    ])


class BroadAirResetHEPAFilterButton(CoordinatorEntity[BroadAirCoordinator], ButtonEntity):
    """Button to reset HEPA filter used time."""

    _attr_has_entity_name = True
    _attr_name = "Reset HEPA Filter"
    _attr_icon = "mdi:air-filter"
    _attr_device_class = ButtonDeviceClass.RESTART

    def __init__(
        self,
        coordinator: BroadAirCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)

        self._device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{self._device_id}_reset_hepa_filter"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
        )

    async def async_press(self) -> None:
        """Handle button press - reset HEPA filter timer."""
        _LOGGER.info("Resetting HEPA filter timer for %s", self._device_id)
        await self.coordinator.client.reset_hepa_filter(self._device_id)
        await self.coordinator.async_request_refresh()


class BroadAirResetCoarseFilterButton(CoordinatorEntity[BroadAirCoordinator], ButtonEntity):
    """Button to reset coarse/primary filter used time."""

    _attr_has_entity_name = True
    _attr_name = "Reset Primary Filter"
    _attr_icon = "mdi:air-filter"
    _attr_device_class = ButtonDeviceClass.RESTART

    def __init__(
        self,
        coordinator: BroadAirCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)

        self._device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{self._device_id}_reset_coarse_filter"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
        )

    async def async_press(self) -> None:
        """Handle button press - reset coarse filter timer."""
        _LOGGER.info("Resetting coarse filter timer for %s", self._device_id)
        await self.coordinator.client.reset_coarse_filter(self._device_id)
        await self.coordinator.async_request_refresh()
