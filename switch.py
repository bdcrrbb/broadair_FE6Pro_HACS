"""Switch platform for Broad Fresh Air."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    DOMAIN,
    FIELD_AUTO_MODE,
    FIELD_SLEEP_MODE,
)
from .coordinator import BroadAirCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BroadAirSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Broad Air switch entity."""

    field: str = ""
    turn_on_fn: Callable[[BroadAirCoordinator, str], Any] | None = None
    turn_off_fn: Callable[[BroadAirCoordinator, str], Any] | None = None


async def _set_sleep_mode(coordinator: BroadAirCoordinator, device_id: str, on: bool) -> None:
    """Set sleep mode."""
    await coordinator.client.set_sleep_mode(device_id, on)


# Note: Auto mode control - if the API supports it with a different sjx command,
# update the api.py and add the method. For now, we'll assume it might use
# a similar pattern. If it doesn't work, we can make this sensor read-only.
SWITCH_DESCRIPTIONS: tuple[BroadAirSwitchEntityDescription, ...] = (
    BroadAirSwitchEntityDescription(
        key="sleep_mode",
        name="Sleep Mode",
        icon="mdi:sleep",
        device_class=SwitchDeviceClass.SWITCH,
        field=FIELD_SLEEP_MODE,
    ),
    # Auto mode - displayed as read-only for now since we don't know the control command
    # If you discover the command, we can make it controllable
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Broad Fresh Air switch entities from config entry."""
    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = [
        BroadAirSleepSwitch(coordinator, entry),
    ]

    # Add auto mode as a read-only binary sensor style display
    # (it's in the switch platform but we only display its state)

    async_add_entities(entities)


class BroadAirSleepSwitch(CoordinatorEntity[BroadAirCoordinator], SwitchEntity):
    """Representation of the sleep mode switch."""

    _attr_has_entity_name = True
    _attr_name = "Sleep Mode"
    _attr_icon = "mdi:sleep"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        coordinator: BroadAirCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity.

        Args:
            coordinator: Data update coordinator
            entry: Config entry
        """
        super().__init__(coordinator)

        self._device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{self._device_id}_sleep_mode"

        # Link to the same device as the fan
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if sleep mode is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(FIELD_SLEEP_MODE) == "1"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        return {
            "auto_mode": self.coordinator.data.get(FIELD_AUTO_MODE) == "1",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on sleep mode."""
        _LOGGER.debug("Enabling sleep mode for %s", self._device_id)

        await self.coordinator.client.set_sleep_mode(self._device_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off sleep mode."""
        _LOGGER.debug("Disabling sleep mode for %s", self._device_id)

        await self.coordinator.client.set_sleep_mode(self._device_id, False)
        await self.coordinator.async_request_refresh()
