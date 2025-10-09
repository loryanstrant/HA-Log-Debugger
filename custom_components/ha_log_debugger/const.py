"""Constants for the Log Debugger for Home Assistant integration."""

DOMAIN = "ha_log_debugger"

# Configuration options
CONF_LOG_LEVEL = "log_level"
CONF_AUTO_ANALYZE = "auto_analyze"
CONF_MAX_AI_CALLS_PER_HOUR = "max_ai_calls_per_hour"
CONF_EXCLUDED_INTEGRATIONS = "excluded_integrations"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_LOG_LEVEL = "WARNING"
DEFAULT_AUTO_ANALYZE = False
DEFAULT_MAX_AI_CALLS = 10
DEFAULT_SCAN_INTERVAL = 30

# Log levels
LOG_LEVELS = ["WARNING", "ERROR", "CRITICAL"]

# Attributes
ATTR_ENTRY_ID = "entry_id"
ATTR_TIMESTAMP = "timestamp"
ATTR_LEVEL = "level"
ATTR_MESSAGE = "message"
ATTR_COMPONENT = "component"
ATTR_ENTITY_ID = "entity_id"
ATTR_DEVICE_ID = "device_id"
ATTR_GITHUB_URL = "github_url"
ATTR_AI_ANALYSIS = "ai_analysis"
ATTR_SUGGESTED_FIX = "suggested_fix"

# Service names
SERVICE_ANALYZE_LOG = "analyze_log_entry"
SERVICE_CLEAR_LOGS = "clear_analyzed_logs"
SERVICE_SCAN_NOW = "scan_logs_now"

# Log scanning limits
MAX_LOG_LINES_FULL_SCAN = 5000
