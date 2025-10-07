# Log Debugger for Home Assistant

A powerful integration that monitors your Home Assistant logs and provides AI-powered explanations for errors and warnings.

**Version:** 0.1.1-alpha (Alpha Release)

## ✨ Key Features

- 🔍 **Real-time Log Monitoring** - Continuously watches for warnings, errors, and critical issues
- 🤖 **AI-Powered Analysis** - Uses Home Assistant's conversation AI to explain errors in plain language
- 📊 **Statistical Tracking** - Monitor error counts, trends, and patterns
- 🔔 **Smart Notifications** - Get persistent notifications with detailed insights
- ⚙️ **Flexible Configuration** - Control what gets monitored and analyzed
- 🎯 **Entity Detection** - Automatically identifies affected entities and devices

## 🚀 Quick Start

1. Install via HACS (custom repository: `loryanstrant/HA-Log-Debugger`)
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services
4. Configure your preferences (log level, AI usage, etc.)
5. View statistics on your dashboard!

## 📖 Documentation

- [Full README](https://github.com/loryanstrant/HA-Log-Debugger/blob/main/README.md)
- [Dashboard Examples](https://github.com/loryanstrant/HA-Log-Debugger/blob/main/DASHBOARD.md)
- [Troubleshooting](https://github.com/loryanstrant/HA-Log-Debugger/blob/main/TROUBLESHOOTING.md)
- [Contributing](https://github.com/loryanstrant/HA-Log-Debugger/blob/main/CONTRIBUTING.md)

## 💡 Example Use Cases

### Template Errors
Identifies template syntax errors and suggests corrections with the exact YAML fix.

### Integration Failures
Explains authentication and configuration issues with step-by-step resolution.

### Energy Dashboard Issues
Pinpoints which sensor is causing energy calculation failures and how to fix it.

### Device Connectivity
Diagnoses offline devices and provides network troubleshooting steps.

## 🎛️ Sensors Provided

- `sensor.log_debugger_total_log_entries` - Total entries monitored
- `sensor.log_debugger_warnings` - Warning count
- `sensor.log_debugger_errors` - Error count
- `sensor.log_debugger_critical_errors` - Critical error count
- `sensor.log_debugger_last_error` - Most recent error with full details
- `sensor.log_debugger_ai_analysis_remaining` - AI calls left this hour

## 🛠️ Services

- `ha_log_debugger.analyze_log_entry` - Analyze specific errors with AI
- `ha_log_debugger.scan_logs_now` - Trigger immediate log scan
- `ha_log_debugger.clear_analyzed_logs` - Clear history and reset counters

## ⚙️ Configuration Options

- **Log Level** - Choose WARNING, ERROR, or CRITICAL
- **Auto-Analyze** - Enable/disable automatic AI analysis
- **AI Call Limit** - Control hourly AI usage (0-100)
- **Scan Interval** - How often to check logs (10-300 seconds)
- **Excluded Integrations** - Skip monitoring for specific integrations

## 🤖 AI Requirements

For best results, configure the Conversation integration with:
- OpenAI (ChatGPT) - Recommended
- Google Generative AI
- Local LLMs (Ollama)
- Any supported AI provider

The integration provides fallback explanations if AI is unavailable.

## ⚠️ Important Notes

- **AI Costs**: Set appropriate rate limits if using paid AI APIs
- **Performance**: Adjust scan interval based on system resources
- **Privacy**: Log data is only sent to AI if auto-analyze is enabled
- **Memory**: Keeps up to 1000 entries in memory

## 🐛 Found a Bug?

[Report it on GitHub](https://github.com/loryanstrant/HA-Log-Debugger/issues)

## 💬 Have Questions?

[Join the Discussion](https://github.com/loryanstrant/HA-Log-Debugger/discussions)

---

**Made with ❤️ for the Home Assistant Community**
