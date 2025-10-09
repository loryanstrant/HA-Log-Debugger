"""Log monitoring and parsing for Log Debugger for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
import os
import re
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import (
    ATTR_AI_ANALYSIS,
    ATTR_COMPONENT,
    ATTR_DEVICE_ID,
    ATTR_ENTITY_ID,
    ATTR_ENTRY_ID,
    ATTR_GITHUB_URL,
    ATTR_LEVEL,
    ATTR_MESSAGE,
    ATTR_SUGGESTED_FIX,
    ATTR_TIMESTAMP,
    CONF_AUTO_ANALYZE,
    CONF_EXCLUDED_INTEGRATIONS,
    CONF_LOG_LEVEL,
    CONF_MAX_AI_CALLS_PER_HOUR,
)
from .parsers import LogParser

_LOGGER = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Represent a parsed log entry."""

    entry_id: str
    timestamp: datetime
    level: str
    message: str
    raw_line: str
    component: str | None = None
    entity_id: str | None = None
    device_id: str | None = None
    github_url: str | None = None
    ai_analysis: str | None = None
    suggested_fix: str | None = None
    analyzed: bool = False
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            ATTR_ENTRY_ID: self.entry_id,
            ATTR_TIMESTAMP: self.timestamp.isoformat(),
            ATTR_LEVEL: self.level,
            ATTR_MESSAGE: self.message,
            ATTR_COMPONENT: self.component,
            ATTR_ENTITY_ID: self.entity_id,
            ATTR_DEVICE_ID: self.device_id,
            ATTR_GITHUB_URL: self.github_url,
            ATTR_AI_ANALYSIS: self.ai_analysis,
            ATTR_SUGGESTED_FIX: self.suggested_fix,
            "analyzed": self.analyzed,
            "context": self.context,
        }


class LogMonitor:
    """Monitor and analyze Home Assistant logs."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the log monitor."""
        self.hass = hass
        self.config_entry = config_entry
        self.log_entries: deque[LogEntry] = deque(maxlen=1000)
        self.last_position = 0
        self.parser = LogParser(hass)
        self._ai_call_count = 0
        self._ai_reset_time = datetime.now()
        self._running = False
        
        # Statistics
        self.total_warnings = 0
        self.total_errors = 0
        self.total_critical = 0

    @property
    def log_file_path(self) -> Path:
        """Get the path to the Home Assistant log file."""
        return Path(self.hass.config.path("home-assistant.log"))

    @property
    def log_level_filter(self) -> str:
        """Get the configured log level filter."""
        return self.config_entry.options.get(
            CONF_LOG_LEVEL,
            self.config_entry.data.get(CONF_LOG_LEVEL, "WARNING"),
        )

    @property
    def auto_analyze(self) -> bool:
        """Check if auto-analysis is enabled."""
        return self.config_entry.options.get(
            CONF_AUTO_ANALYZE,
            self.config_entry.data.get(CONF_AUTO_ANALYZE, False),
        )

    @property
    def max_ai_calls_per_hour(self) -> int:
        """Get max AI calls per hour."""
        return self.config_entry.options.get(
            CONF_MAX_AI_CALLS_PER_HOUR,
            self.config_entry.data.get(CONF_MAX_AI_CALLS_PER_HOUR, 10),
        )

    @property
    def excluded_integrations(self) -> list[str]:
        """Get list of excluded integrations."""
        return self.config_entry.options.get(CONF_EXCLUDED_INTEGRATIONS, [])

    def _reset_ai_counter_if_needed(self) -> None:
        """Reset AI call counter if an hour has passed."""
        now = datetime.now()
        if now - self._ai_reset_time > timedelta(hours=1):
            self._ai_call_count = 0
            self._ai_reset_time = now

    def _can_use_ai(self) -> bool:
        """Check if we can make another AI call."""
        self._reset_ai_counter_if_needed()
        return self._ai_call_count < self.max_ai_calls_per_hour

    def _should_process_level(self, level: str) -> bool:
        """Check if this log level should be processed."""
        level_priority = {"WARNING": 1, "ERROR": 2, "CRITICAL": 3}
        configured_priority = level_priority.get(self.log_level_filter, 1)
        message_priority = level_priority.get(level.upper(), 0)
        return message_priority >= configured_priority

    async def async_start(self) -> None:
        """Start monitoring logs."""
        self._running = True
        _LOGGER.info("Log monitor started")
        
        # Initialize file position
        if await self.hass.async_add_executor_job(self.log_file_path.exists):
            self.last_position = await self.hass.async_add_executor_job(
                lambda: self.log_file_path.stat().st_size
            )

    async def async_stop(self) -> None:
        """Stop monitoring logs."""
        self._running = False
        _LOGGER.info("Log monitor stopped")

    async def async_scan_logs(self, full_scan: bool = False) -> None:
        """Scan log file for entries.
        
        Args:
            full_scan: If True, scan entire log file. If False, only read new entries since last position.
        """
        if not await self.hass.async_add_executor_job(self.log_file_path.exists):
            _LOGGER.warning("Log file not found: %s", self.log_file_path)
            return

        try:
            file_size = await self.hass.async_add_executor_job(
                lambda: self.log_file_path.stat().st_size
            )
            
            # If file was rotated or truncated, reset position
            if file_size < self.last_position:
                self.last_position = 0
                _LOGGER.info("Log file rotated, resetting position")
            
            # Read lines using executor
            if full_scan:
                _LOGGER.info("Performing full log scan")
                new_lines = await self.hass.async_add_executor_job(
                    self._read_full_log
                )
            else:
                new_lines = await self.hass.async_add_executor_job(
                    self._read_log_lines
                )
            
            # Process new lines
            if new_lines:
                _LOGGER.info("Processing %d log lines", len(new_lines))
                await self._process_log_lines(new_lines)
            else:
                _LOGGER.debug("No new log entries to process")
                
        except Exception as e:
            _LOGGER.error("Error scanning logs: %s", e, exc_info=True)

    def _read_log_lines(self) -> list[str]:
        """Read new lines from log file since last position (runs in executor)."""
        with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()
        return new_lines

    def _read_full_log(self) -> list[str]:
        """Read entire log file (runs in executor).
        
        Reads the last 5000 lines or the entire file if smaller.
        Updates last_position to end of file.
        """
        with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Read all lines
            all_lines = f.readlines()
            # Take last 5000 lines to avoid overwhelming the system
            lines_to_process = all_lines[-5000:] if len(all_lines) > 5000 else all_lines
            # Update position to end of file
            f.seek(0, 2)  # Seek to end
            self.last_position = f.tell()
        return lines_to_process


    async def _process_log_lines(self, lines: list[str]) -> None:
        """Process new log lines."""
        for line in lines:
            try:
                entry = await self._parse_log_line(line)
                if entry:
                    self.log_entries.append(entry)
                    self._update_statistics(entry)
                    
                    # Auto-analyze if enabled
                    if self.auto_analyze and self._can_use_ai():
                        await self.async_analyze_entry(entry.entry_id, use_ai=True)
                    
                    # Send notification for critical errors
                    if entry.level == "CRITICAL" or entry.level == "ERROR":
                        await self._send_notification(entry)
                        
            except Exception as e:
                _LOGGER.debug("Error processing log line: %s - %s", line[:100], e)

    async def _parse_log_line(self, line: str) -> LogEntry | None:
        """Parse a single log line."""
        # Basic regex to match Home Assistant log format
        # Format: YYYY-MM-DD HH:MM:SS LEVEL (component) [source] message
        pattern = r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+\(([^)]+)\)\s+\[([^\]]+)\]\s+(.+)$"
        match = re.match(pattern, line.strip())
        
        if not match:
            return None
        
        timestamp_str, level, component, source, message = match.groups()
        
        # Check if we should process this level
        if not self._should_process_level(level):
            return None
        
        # Check if component is excluded
        if component in self.excluded_integrations:
            return None
        
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = datetime.now()
        
        # Create entry
        entry_id = f"{timestamp.timestamp()}_{hash(line) % 10000}"
        entry = LogEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            level=level,
            message=message,
            raw_line=line,
            component=component,
        )
        
        # Parse additional details
        await self.parser.parse_entry(entry)
        
        return entry

    def _update_statistics(self, entry: LogEntry) -> None:
        """Update statistics counters."""
        if entry.level == "WARNING":
            self.total_warnings += 1
        elif entry.level == "ERROR":
            self.total_errors += 1
        elif entry.level == "CRITICAL":
            self.total_critical += 1

    async def async_analyze_entry(self, entry_id: str, use_ai: bool = True) -> None:
        """Analyze a specific log entry."""
        # Find the entry
        entry = next((e for e in self.log_entries if e.entry_id == entry_id), None)
        if not entry:
            _LOGGER.warning("Log entry not found: %s", entry_id)
            return
        
        if entry.analyzed:
            _LOGGER.debug("Entry already analyzed: %s", entry_id)
            return
        
        # Use AI if requested and available
        if use_ai and self._can_use_ai():
            from .ai_analyzer import AIAnalyzer
            
            analyzer = AIAnalyzer(self.hass)
            analysis = await analyzer.analyze_log_entry(entry)
            
            if analysis:
                entry.ai_analysis = analysis.get("explanation")
                entry.suggested_fix = analysis.get("solution")
                entry.analyzed = True
                self._ai_call_count += 1
                
                _LOGGER.info("AI analysis completed for entry: %s", entry_id)
                
                # Update notification with AI insights
                await self._send_notification(entry)

    async def _send_notification(self, entry: LogEntry) -> None:
        """Send a persistent notification for a log entry."""
        title = f"{entry.level}: {entry.component or 'Unknown'}"
        
        message_parts = [f"**Message:** {entry.message[:200]}"]
        
        if entry.entity_id:
            message_parts.append(f"**Entity:** `{entry.entity_id}`")
        
        if entry.device_id:
            message_parts.append(f"**Device ID:** `{entry.device_id}`")
        
        if entry.github_url:
            message_parts.append(f"**Repository:** {entry.github_url}")
        
        if entry.ai_analysis:
            message_parts.append(f"\n**AI Analysis:**\n{entry.ai_analysis}")
        
        if entry.suggested_fix:
            message_parts.append(f"\n**Suggested Fix:**\n```yaml\n{entry.suggested_fix[:500]}\n```")
        
        message = "\n\n".join(message_parts)
        
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": title,
                "message": message,
                "notification_id": f"log_debugger_{entry.entry_id}",
            },
        )

    async def async_clear_history(self) -> None:
        """Clear the log entry history."""
        self.log_entries.clear()
        self.total_warnings = 0
        self.total_errors = 0
        self.total_critical = 0
        _LOGGER.info("Log history cleared")

    def get_recent_entries(self, count: int = 50) -> list[LogEntry]:
        """Get recent log entries."""
        return list(self.log_entries)[-count:]

    def get_statistics(self) -> dict[str, Any]:
        """Get current statistics."""
        return {
            "total_entries": len(self.log_entries),
            "total_warnings": self.total_warnings,
            "total_errors": self.total_errors,
            "total_critical": self.total_critical,
            "ai_calls_remaining": max(
                0, self.max_ai_calls_per_hour - self._ai_call_count
            ),
        }
