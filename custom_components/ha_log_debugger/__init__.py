"""The Log Debugger for Home Assistant integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .log_monitor import LogMonitor

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


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
    
    # Get scan interval from config (in seconds)
    scan_interval_seconds = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    scan_interval = timedelta(seconds=scan_interval_seconds)
    
    _LOGGER.info(
        "Log Debugger: Periodic scanning enabled every %d seconds",
        scan_interval_seconds
    )
    
    # Schedule periodic log checks (incremental scans)
    async def periodic_scan(now):
        """Scan logs periodically for new entries."""
        await log_monitor.async_scan_logs(full_scan=False)
    
    entry.async_on_unload(
        async_track_time_interval(hass, periodic_scan, scan_interval)
    )
    
    # Do an initial full scan on startup
    await log_monitor.async_scan_logs(full_scan=True)
    
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
        """Manually trigger a full log scan."""
        _LOGGER.info("Manual full log scan triggered")
        await log_monitor.async_scan_logs(full_scan=True)
    
    hass.services.async_register(
        DOMAIN, "analyze_log_entry", analyze_log_entry
    )
    hass.services.async_register(
        DOMAIN, "clear_analyzed_logs", clear_analyzed_logs
    )
    hass.services.async_register(
        DOMAIN, "scan_logs_now", scan_logs_now
    )
