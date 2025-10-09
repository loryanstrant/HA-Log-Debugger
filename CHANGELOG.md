# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-alpha] - 2025-10-09

### Added
- Full log scan capability - `scan_logs_now` service now scans last 5000 lines instead of only new entries
- Configurable periodic scanning with `scan_interval` option (10-300 seconds, default 30)
- Initial full scan on integration startup
- Added scan_interval configuration to initial setup flow
- Improved logging with detailed scan progress messages

### Fixed
- Fixed OptionsFlowHandler initialization to properly accept config_entry parameter
- Fixed log scanning to support both full scans (manual) and incremental scans (periodic)
- Cleared Python bytecode cache to ensure latest code runs

### Changed
- Removed firmware version (sw_version) from device info - not relevant for software integrations
- Manual scan service now performs full log file scan by default
- Periodic background scanning only reads new entries for efficiency
- Improved service responsiveness and reliability

### Technical
- Refactored `async_scan_logs()` to accept `full_scan` parameter
- Added `_read_full_log()` method for complete log file scanning
- Updated `__init__.py` to use configurable scan interval from config entry

## [0.1.1-alpha] - 2025-10-07

### Fixed
- Removed deprecated explicit config_entry assignment in OptionsFlowHandler to fix Home Assistant 2025.12 deprecation warning
- Converted blocking file I/O operations to async executor pattern to fix blocking call warnings

## [0.1.0-alpha] - 2025-10-07

### Added
- Initial alpha release of Log Debugger for Home Assistant
- Real-time log monitoring for warnings, errors, and critical messages
- AI-powered log analysis using Home Assistant conversation integration
- Automatic entity and device identification from log messages
- Pattern matching for common error types
- GitHub integration repository linking
- Persistent notifications for critical errors
- Six sensor entities for statistics tracking
- Three services: analyze_log_entry, clear_analyzed_logs, scan_logs_now
- Configurable options via UI
- HACS-compatible structure

### Features
- Monitor Home Assistant logs in real-time
- Identify warnings, errors, and critical messages
- Extract entity IDs, device IDs, and component information
- AI-powered explanations and solutions
- Automatic GitHub repository detection
- Customizable log level filtering
- Auto-analysis toggle
- Rate limiting for AI calls
- Integration exclusion list
