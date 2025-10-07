"""Log entry parsing and pattern matching."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

if TYPE_CHECKING:
    from .log_monitor import LogEntry

# Known integration GitHub repositories
INTEGRATION_REPOS = {
    "homeassistant": "https://github.com/home-assistant/core",
    "esphome": "https://github.com/esphome/esphome",
    "hass": "https://github.com/home-assistant/core",
    "mqtt": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/mqtt",
    "zha": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/zha",
    "zigbee": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/zha",
    "rest": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/rest",
    "template": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/template",
    "automation": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/automation",
    "script": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/script",
    "sensor": "https://github.com/home-assistant/core/tree/dev/homeassistant/components/sensor",
}


class LogParser:
    """Parse and extract information from log entries."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the parser."""
        self.hass = hass
        self._entity_registry = None
        self._device_registry = None

    @property
    def entity_registry(self) -> er.EntityRegistry:
        """Get entity registry."""
        if self._entity_registry is None:
            self._entity_registry = er.async_get(self.hass)
        return self._entity_registry

    @property
    def device_registry(self) -> dr.DeviceRegistry:
        """Get device registry."""
        if self._device_registry is None:
            self._device_registry = dr.async_get(self.hass)
        return self._device_registry

    async def parse_entry(self, entry: LogEntry) -> None:
        """Parse a log entry and extract relevant information."""
        # Extract entity IDs
        entity_id = self._extract_entity_id(entry.message)
        if entity_id:
            entry.entity_id = entity_id
            
            # Try to get device from entity
            entity = self.entity_registry.async_get(entity_id)
            if entity and entity.device_id:
                entry.device_id = entity.device_id
                
                # Get device info
                device = self.device_registry.async_get(entity.device_id)
                if device:
                    entry.context["device_name"] = device.name_by_user or device.name
                    entry.context["manufacturer"] = device.manufacturer
                    entry.context["model"] = device.model

        # Extract GitHub URL
        if entry.component:
            entry.github_url = self._get_github_url(entry.component)

        # Extract additional context
        self._extract_context(entry)

    def _extract_entity_id(self, message: str) -> str | None:
        """Extract entity ID from log message."""
        # Pattern: domain.entity_name
        patterns = [
            r"entity[:\s]+([a-z_]+\.[a-z0-9_]+)",
            r"'([a-z_]+\.[a-z0-9_]+)'",
            r"`([a-z_]+\.[a-z0-9_]+)`",
            r"\b([a-z_]+\.[a-z0-9_]+)\b",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entity_id = match.group(1)
                # Validate it's a real entity format
                if "." in entity_id and len(entity_id.split(".")) == 2:
                    # Check if entity exists
                    if self.entity_registry.async_get(entity_id):
                        return entity_id
        
        return None

    def _get_github_url(self, component: str) -> str | None:
        """Get GitHub URL for a component."""
        # Check known repos
        component_lower = component.lower()
        
        # Direct match
        if component_lower in INTEGRATION_REPOS:
            return INTEGRATION_REPOS[component_lower]
        
        # Try to find custom component pattern
        if component_lower.startswith("custom_components."):
            custom_comp = component_lower.replace("custom_components.", "")
            # Can't know the actual repo, but provide a search link
            return f"https://github.com/search?q={custom_comp}+home+assistant"
        
        # Default to core component path
        return f"https://github.com/home-assistant/core/tree/dev/homeassistant/components/{component_lower}"

    def _extract_context(self, entry: LogEntry) -> None:
        """Extract additional context from the log message."""
        message = entry.message.lower()
        
        # Common error patterns and their explanations
        patterns = {
            "unknown": {
                "pattern": r"(state|value).*unknown",
                "explanation": "A sensor or entity has an 'unknown' state, usually because it hasn't received data yet or the source is unavailable.",
            },
            "unavailable": {
                "pattern": r"(state|entity).*unavailable",
                "explanation": "An entity is unavailable, typically because the device is offline or the integration cannot communicate with it.",
            },
            "timeout": {
                "pattern": r"timeout|timed out",
                "explanation": "A connection or operation exceeded the allowed time limit. This often indicates network issues or an overloaded device.",
            },
            "connection": {
                "pattern": r"connection.*(?:refused|failed|error|reset)",
                "explanation": "Failed to establish a connection to a device or service. Check network connectivity and service availability.",
            },
            "template": {
                "pattern": r"template.*error|error.*rendering",
                "explanation": "A Jinja2 template has an error. This is usually due to referencing undefined variables or incorrect syntax.",
            },
            "energy": {
                "pattern": r"energy.*calculation|calculate.*energy",
                "explanation": "Energy calculation failed, often because one or more energy sensors have invalid or missing values.",
            },
            "setup": {
                "pattern": r"setup.*failed|failed.*setup",
                "explanation": "An integration or component failed to set up properly. Check the configuration and logs for more details.",
            },
            "authentication": {
                "pattern": r"auth(?:entication)?.*(?:failed|error)|invalid.*(?:token|key|password|credentials)",
                "explanation": "Authentication failed. Check your credentials, API keys, or tokens for this integration.",
            },
        }
        
        for error_type, info in patterns.items():
            if re.search(info["pattern"], message):
                entry.context["error_type"] = error_type
                entry.context["basic_explanation"] = info["explanation"]
                break
        
        # Extract numbers that might be relevant
        numbers = re.findall(r"\b\d+\.?\d*\b", entry.message)
        if numbers:
            entry.context["numbers"] = numbers
        
        # Extract file paths
        file_paths = re.findall(r"[/\\][\w/\\.-]+\.\w+", entry.message)
        if file_paths:
            entry.context["file_paths"] = file_paths
        
        # Extract IP addresses
        ip_addresses = re.findall(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b", entry.message
        )
        if ip_addresses:
            entry.context["ip_addresses"] = ip_addresses
        
        # Extract URLs
        urls = re.findall(
            r"https?://[^\s]+", entry.message
        )
        if urls:
            entry.context["urls"] = urls
