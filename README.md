# Log Debugger for Home Assistant

```
╔══════════════════════════════6. Go to Settings → Devices & Services → Add Integration
7. Search for "Log Debugger"═══════════════════════════════════╗
║                                                                   ║
║   █░░ █▀█ █▀▀   █▀▄ █▀▀ █▄▄ █░█ █▀▀ █▀▀ █▀▀ █▀█                ║
║   █▄▄ █▄█ █▄█   █▄▀ ██▄ █▄█ █▄█ █▄█ █▄█ ██▄ █▀▄                ║
║                                                                   ║
║   ┌─────────────────────────────────────────────────────────┐   ║
║   │  📋 Monitor Logs  →  🔍 Detect Issues  →  🤖 AI Analysis │   ║
║   └─────────────────────────────────────────────────────────┘   ║
║                                                                   ║
║   🎯 Automatically identifies errors & warnings in your logs      ║
║   💡 Explains technical issues in plain language                 ║
║   🔧 Suggests actionable fixes with code examples                ║
║   📊 Tracks statistics & trends over time                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/loryanstrant/HA-Log-Debugger.svg)](https://github.com/loryanstrant/HA-Log-Debugger/releases)
[![License](https://img.shields.io/github/license/loryanstrant/HA-Log-Debugger.svg)](LICENSE)

A powerful custom integration that monitors your Home Assistant log files for warnings and errors, providing AI-powered explanations and solutions in plain language.

## Features

🔍 **Intelligent Log Monitoring**
- Continuously monitors `home-assistant.log` for warnings, errors, and critical messages
- Automatically identifies affected integrations, entities, and devices
- Extracts relevant context from log messages

🤖 **AI-Powered Analysis**
- Leverages Home Assistant's built-in conversation/AI capabilities
- Translates technical errors into plain language explanations
- Provides step-by-step troubleshooting instructions
- Suggests corrected YAML configurations when applicable

📊 **Real-time Statistics**
- Sensor entities tracking warning, error, and critical counts
- Last error details with full context
- AI analysis call tracking to manage costs

🔔 **Smart Notifications**
- Persistent notifications for errors and critical issues
- Includes entity IDs, device information, and GitHub links
- Shows AI analysis and suggested fixes directly in notifications

⚙️ **Flexible Configuration**
- Configure minimum log level to monitor (WARNING, ERROR, CRITICAL)
- Control AI auto-analysis with hourly rate limits
- Exclude specific integrations from monitoring
- Adjustable scan intervals

🛠️ **Powerful Services**
- `ha_log_debugger.analyze_log_entry` - Manually analyze specific log entries
- `ha_log_debugger.scan_logs_now` - Trigger immediate log scan
- `ha_log_debugger.clear_analyzed_logs` - Clear history and reset counters

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/loryanstrant/HA-Log-Debugger` as an Integration
5. Click "Install"
6. Restart Home Assistant
7. Go to Settings → Devices & Services → Add Integration
8. Search for "Home Assistant Log Debugger"

### Manual Installation

1. Copy the `custom_components/ha_log_debugger` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Log Debugger"

## Configuration

### Initial Setup

1. Add the integration through the UI (Settings → Devices & Services → Add Integration)
2. Configure the following options:
   - **Minimum Log Level**: Choose WARNING, ERROR, or CRITICAL
   - **Auto Analyze**: Enable/disable automatic AI analysis of new errors
   - **Max AI Calls per Hour**: Set a limit to control AI usage (default: 10)

### Options

You can modify these settings anytime by clicking "Configure" on the integration:

- **Log Level**: Minimum severity to monitor
- **Auto Analyze**: Automatically analyze new errors with AI
- **Max AI Calls per Hour**: Prevent excessive AI usage (0-100)
- **Scan Interval**: How often to check logs in seconds (10-300)
- **Excluded Integrations**: Comma-separated list of integrations to ignore

## Usage

### Sensors

The integration creates several sensor entities:

- `sensor.log_debugger_total_log_entries` - Total monitored entries
- `sensor.log_debugger_warnings` - Warning count
- `sensor.log_debugger_errors` - Error count
- `sensor.log_debugger_critical_errors` - Critical error count
- `sensor.log_debugger_last_error` - Most recent error with full details
- `sensor.log_debugger_ai_analysis_remaining` - AI calls remaining this hour

### Services

#### Analyze a Specific Log Entry

```yaml
service: ha_log_debugger.analyze_log_entry
data:
  entry_id: "1696723200.0_1234"
  use_ai: true
```

#### Manually Scan Logs

```yaml
service: ha_log_debugger.scan_logs_now
```

#### Clear History

```yaml
service: ha_log_debugger.clear_analyzed_logs
```

### Automations

**Example: Notify on Critical Errors**

```yaml
automation:
  - alias: "Alert on Critical Errors"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_critical_errors
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Critical Error Detected"
          message: "{{ state_attr('sensor.log_debugger_last_error', 'full_message') }}"
```

**Example: Auto-Analyze Errors During Off-Peak Hours**

```yaml
automation:
  - alias: "Auto-Analyze Errors at Night"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_errors
    condition:
      - condition: time
        after: "22:00:00"
        before: "06:00:00"
      - condition: template
        value_template: "{{ states('sensor.log_debugger_ai_analysis_remaining') | int > 0 }}"
    action:
      - service: ha_log_debugger.analyze_log_entry
        data:
          entry_id: "{{ state_attr('sensor.log_debugger_last_error', 'entry_id') }}"
          use_ai: true
```

## AI Analysis

The integration uses Home Assistant's built-in conversation/AI capabilities. For best results:

1. **Configure an AI Provider**: Set up the Conversation integration with:
   - OpenAI (ChatGPT)
   - Google Generative AI
   - Local LLMs via Ollama
   - Any other supported AI provider

2. **Rate Limiting**: Set appropriate AI call limits based on your:
   - API costs/quotas
   - Home Assistant stability
   - Frequency of errors

3. **Fallback Analysis**: If AI is unavailable, the integration provides:
   - Pattern-based explanations
   - Common troubleshooting steps
   - Links to relevant documentation

## Common Use Cases

### Template Errors
The integration identifies template syntax errors and suggests corrections:
- Shows which entity caused the issue
- Provides corrected template syntax
- Links to Home Assistant templating docs

### Integration Failures
When an integration fails to set up:
- Identifies authentication/configuration issues
- Suggests credential verification steps
- Links to the integration's GitHub repository

### Energy Calculation Errors
For energy dashboard issues:
- Identifies which sensor has invalid values
- Explains state requirements (numeric, not "unknown")
- Suggests fixes like availability templates

### Device Connectivity
When devices go offline:
- Shows which device/entity is affected
- Provides network troubleshooting steps
- Suggests integration restart procedures

## Troubleshooting

### Integration Not Finding Errors

- **Check Log Level**: Ensure your `log_level` setting captures the errors
- **Verify Log Location**: The integration looks for `home-assistant.log` in your config directory
- **Check Excluded Integrations**: Make sure you haven't excluded the problematic integration

### AI Analysis Not Working

- **Conversation Integration**: Ensure the Conversation integration is set up
- **AI Provider**: Configure an AI provider (OpenAI, Google, etc.)
- **Rate Limit**: Check if you've hit the hourly AI call limit
- **Check Sensor**: View `sensor.log_debugger_ai_analysis_remaining`

### High Memory Usage

- **Reduce History**: The integration keeps up to 1000 entries in memory
- **Increase Scan Interval**: Scan less frequently (e.g., 60 seconds)
- **Exclude Verbose Integrations**: Exclude chatty integrations that log frequently

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/loryanstrant/HA-Log-Debugger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/loryanstrant/HA-Log-Debugger/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## Acknowledgments

- Home Assistant Community for inspiration and feedback
- All contributors who help improve this integration

## Disclaimer

This integration analyzes log files to help with debugging. While it provides helpful suggestions:
- Always verify suggested fixes before applying them
- AI analysis may not always be accurate
- Back up your configuration before making changes
- Use at your own risk

---

---

**Version:** 0.2.0-alpha (Alpha Release)

**Made with ❤️ for the Home Assistant Community**
