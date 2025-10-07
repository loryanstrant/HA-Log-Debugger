"""Sensor platform for Log Debugger for Home Assistant."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    log_monitor = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        LogDebuggerTotalSensor(log_monitor, config_entry),
        LogDebuggerWarningSensor(log_monitor, config_entry),
        LogDebuggerErrorSensor(log_monitor, config_entry),
        LogDebuggerCriticalSensor(log_monitor, config_entry),
        LogDebuggerLastErrorSensor(log_monitor, config_entry),
        LogDebuggerAICallsSensor(log_monitor, config_entry),
    ]

    async_add_entities(sensors)


class LogDebuggerBaseSensor(SensorEntity):
    """Base class for log debugger sensors."""

    _attr_has_entity_name = True

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self.log_monitor = log_monitor
        self._config_entry = config_entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Log Debugger",
            "manufacturer": "Home Assistant Community",
            "model": "Log Debugger",
            "sw_version": "0.1.1-alpha",
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity added to hass."""
        await super().async_added_to_hass()
        # Force an update when added
        self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        """Update the sensor."""
        # Override in subclasses
        pass


class LogDebuggerTotalSensor(LogDebuggerBaseSensor):
    """Sensor showing total log entries."""

    _attr_name = "Total Log Entries"
    _attr_icon = "mdi:text-box-multiple"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(log_monitor, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_total_entries"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        stats = self.log_monitor.get_statistics()
        return stats.get("total_entries", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self.log_monitor.get_statistics()
        return {
            "warnings": stats.get("total_warnings", 0),
            "errors": stats.get("total_errors", 0),
            "critical": stats.get("total_critical", 0),
        }


class LogDebuggerWarningSensor(LogDebuggerBaseSensor):
    """Sensor showing warning count."""

    _attr_name = "Warnings"
    _attr_icon = "mdi:alert"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(log_monitor, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_warnings"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.log_monitor.total_warnings


class LogDebuggerErrorSensor(LogDebuggerBaseSensor):
    """Sensor showing error count."""

    _attr_name = "Errors"
    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(log_monitor, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_errors"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.log_monitor.total_errors


class LogDebuggerCriticalSensor(LogDebuggerBaseSensor):
    """Sensor showing critical error count."""

    _attr_name = "Critical Errors"
    _attr_icon = "mdi:alert-octagon"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(log_monitor, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_critical"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.log_monitor.total_critical


class LogDebuggerLastErrorSensor(LogDebuggerBaseSensor):
    """Sensor showing the last error message."""

    _attr_name = "Last Error"
    _attr_icon = "mdi:message-alert"

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(log_monitor, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_last_error"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        recent_entries = self.log_monitor.get_recent_entries(count=10)
        
        # Find the most recent error or critical
        for entry in reversed(recent_entries):
            if entry.level in ["ERROR", "CRITICAL"]:
                return entry.message[:255]  # Limit length
        
        return "No recent errors"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        recent_entries = self.log_monitor.get_recent_entries(count=10)
        
        # Find the most recent error or critical
        for entry in reversed(recent_entries):
            if entry.level in ["ERROR", "CRITICAL"]:
                attrs = {
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "component": entry.component,
                    "full_message": entry.message,
                }
                
                if entry.entity_id:
                    attrs["entity_id"] = entry.entity_id
                if entry.device_id:
                    attrs["device_id"] = entry.device_id
                if entry.github_url:
                    attrs["github_url"] = entry.github_url
                if entry.ai_analysis:
                    attrs["ai_analysis"] = entry.ai_analysis
                if entry.suggested_fix:
                    attrs["suggested_fix"] = entry.suggested_fix
                
                return attrs
        
        return {}


class LogDebuggerAICallsSensor(LogDebuggerBaseSensor):
    """Sensor showing remaining AI analysis calls."""

    _attr_name = "AI Analysis Remaining"
    _attr_icon = "mdi:robot"

    def __init__(self, log_monitor, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(log_monitor, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_ai_calls"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        stats = self.log_monitor.get_statistics()
        return stats.get("ai_calls_remaining", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "max_calls_per_hour": self.log_monitor.max_ai_calls_per_hour,
            "auto_analyze_enabled": self.log_monitor.auto_analyze,
        }
