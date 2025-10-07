"""The Log Debugger for Home Assistant integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .log_monitor import LogMonitor

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Log Debugger for Home Assistant from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize the log monitor
    log_monitor = LogMonitor(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = log_monitor
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Start monitoring logs
    await log_monitor.async_start()
    
    # Register services
    await async_setup_services(hass, log_monitor)
    
    # Schedule periodic log checks
    async def periodic_scan(now):
        """Scan logs periodically."""
        await log_monitor.async_scan_logs()
    
    entry.async_on_unload(
        async_track_time_interval(hass, periodic_scan, SCAN_INTERVAL)
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        log_monitor = hass.data[DOMAIN].pop(entry.entry_id)
        await log_monitor.async_stop()
    
    return unload_ok


async def async_setup_services(hass: HomeAssistant, log_monitor: LogMonitor) -> None:
    """Set up services for the integration."""
    
    async def analyze_log_entry(call: ServiceCall) -> None:
        """Analyze a specific log entry with AI."""
        entry_id = call.data.get("entry_id")
        use_ai = call.data.get("use_ai", True)
        
        await log_monitor.async_analyze_entry(entry_id, use_ai)
    
    async def clear_analyzed_logs(call: ServiceCall) -> None:
        """Clear the history of analyzed logs."""
        await log_monitor.async_clear_history()
    
    async def scan_logs_now(call: ServiceCall) -> None:
        """Manually trigger a log scan."""
        await log_monitor.async_scan_logs()
    
    hass.services.async_register(
        DOMAIN, "analyze_log_entry", analyze_log_entry
    )
    hass.services.async_register(
        DOMAIN, "clear_analyzed_logs", clear_analyzed_logs
    )
    hass.services.async_register(
        DOMAIN, "scan_logs_now", scan_logs_now
    )
