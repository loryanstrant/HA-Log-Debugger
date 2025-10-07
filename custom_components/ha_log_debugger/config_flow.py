"""Config flow for Log Debugger for Home Assistant integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_AUTO_ANALYZE,
    CONF_EXCLUDED_INTEGRATIONS,
    CONF_LOG_LEVEL,
    CONF_MAX_AI_CALLS_PER_HOUR,
    CONF_SCAN_INTERVAL,
    DEFAULT_AUTO_ANALYZE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_AI_CALLS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOG_LEVELS,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Log Debugger for Home Assistant."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Only allow one instance
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_LOG_LEVEL, default=DEFAULT_LOG_LEVEL
                        ): vol.In(LOG_LEVELS),
                        vol.Optional(
                            CONF_AUTO_ANALYZE, default=DEFAULT_AUTO_ANALYZE
                        ): bool,
                        vol.Optional(
                            CONF_MAX_AI_CALLS_PER_HOUR, default=DEFAULT_MAX_AI_CALLS
                        ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                    }
                ),
            )

        return self.async_create_entry(
            title="Log Debugger",
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the component."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Process excluded integrations string
            if CONF_EXCLUDED_INTEGRATIONS in user_input:
                excluded = user_input[CONF_EXCLUDED_INTEGRATIONS]
                if isinstance(excluded, str):
                    user_input[CONF_EXCLUDED_INTEGRATIONS] = [
                        x.strip() for x in excluded.split(",") if x.strip()
                    ]
            
            return self.async_create_entry(title="", data=user_input)

        # Get current options or defaults
        current_log_level = self.config_entry.options.get(
            CONF_LOG_LEVEL, self.config_entry.data.get(CONF_LOG_LEVEL, DEFAULT_LOG_LEVEL)
        )
        current_auto_analyze = self.config_entry.options.get(
            CONF_AUTO_ANALYZE,
            self.config_entry.data.get(CONF_AUTO_ANALYZE, DEFAULT_AUTO_ANALYZE),
        )
        current_max_calls = self.config_entry.options.get(
            CONF_MAX_AI_CALLS_PER_HOUR,
            self.config_entry.data.get(CONF_MAX_AI_CALLS_PER_HOUR, DEFAULT_MAX_AI_CALLS),
        )
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        current_excluded = self.config_entry.options.get(
            CONF_EXCLUDED_INTEGRATIONS, []
        )
        excluded_str = ", ".join(current_excluded) if current_excluded else ""

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LOG_LEVEL, default=current_log_level): vol.In(
                        LOG_LEVELS
                    ),
                    vol.Optional(
                        CONF_AUTO_ANALYZE, default=current_auto_analyze
                    ): bool,
                    vol.Optional(
                        CONF_MAX_AI_CALLS_PER_HOUR, default=current_max_calls
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=current_scan_interval
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
                    vol.Optional(
                        CONF_EXCLUDED_INTEGRATIONS, default=excluded_str
                    ): str,
                }
            ),
        )
