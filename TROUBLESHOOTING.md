# Troubleshooting Guide

This guide helps you resolve common issues with the Log Debugger for Home Assistant integration.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Integration Not Loading](#integration-not-loading)
- [Log Monitoring Issues](#log-monitoring-issues)
- [AI Analysis Issues](#ai-analysis-issues)
- [Performance Issues](#performance-issues)
- [Sensor Issues](#sensor-issues)
- [Service Issues](#service-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Integration Not Appearing in HACS

**Problem:** Can't find the integration in HACS after adding custom repository.

**Solutions:**
1. Ensure you added it as an "Integration" not "Plugin"
2. Refresh the HACS page (hard refresh: Ctrl+Shift+R)
3. Check the repository URL is correct: `https://github.com/loryanstrant/HA-Log-Debugger`
4. Verify HACS is up to date

### Integration Not Appearing in Add Integration Menu

**Problem:** Can't find "Log Debugger" when adding integration.

**Solutions:**
1. Restart Home Assistant after installation
2. Clear browser cache
3. Check the integration was installed correctly:
   ```bash
   ls -la /config/custom_components/ha_log_debugger/
   ```
4. Check for errors in Home Assistant logs during startup

## Integration Not Loading

### Check Logs for Errors

Look in `Configuration → Logs` or `home-assistant.log` for errors like:

```
Error loading custom integration ha_log_debugger
```

**Common Causes:**
- Missing dependencies
- Python syntax errors
- File permission issues

**Solutions:**
1. Reinstall the integration via HACS
2. Check file permissions:
   ```bash
   chmod -R 755 /config/custom_components/ha_log_debugger/
   ```
3. Verify all files are present (see file list below)

### Required Files

```
custom_components/ha_log_debugger/
├── __init__.py
├── ai_analyzer.py
├── config_flow.py
├── const.py
├── log_monitor.py
├── manifest.json
├── parsers.py
├── sensor.py
├── services.yaml
├── strings.json
└── translations/
    └── en.json
```

## Log Monitoring Issues

### No Errors Being Detected

**Problem:** Integration runs but doesn't detect any errors.

**Possible Causes:**
1. Log level filter too high
2. Log file not being read
3. Logs being excluded

**Solutions:**

1. **Check Log Level Setting:**
   - Go to Settings → Devices & Services → Log Debugger → Configure
   - Lower the log level (try "WARNING")

2. **Verify Log File Location:**
   ```bash
   ls -la /config/home-assistant.log
   ```

3. **Check Excluded Integrations:**
   - In configuration, check if the problem integration is excluded

4. **Manually Trigger Scan:**
   ```yaml
   service: ha_log_debugger.scan_logs_now
   ```

5. **Check Sensor State:**
   ```yaml
   Developer Tools → States → sensor.log_debugger_total_log_entries
   ```

### Log File Permission Issues

**Problem:** Integration can't read the log file.

**Error in Logs:**
```
Error scanning logs: Permission denied
```

**Solution:**
```bash
chmod 644 /config/home-assistant.log
```

### Log Rotation Issues

**Problem:** Integration stops working after log rotation.

**Solution:**
The integration automatically detects log rotation. If it doesn't:
1. Restart Home Assistant
2. Manually trigger a scan

## AI Analysis Issues

### AI Analysis Not Working

**Problem:** Auto-analysis enabled but no AI insights appear.

**Diagnostic Steps:**

1. **Check Conversation Integration:**
   ```yaml
   # Developer Tools → Services
   service: conversation.process
   data:
     text: "Test"
   ```
   
   If this fails, Conversation isn't set up properly.

2. **Check AI Call Limit:**
   - View `sensor.log_debugger_ai_analysis_remaining`
   - If 0, you've hit the hourly limit
   - Wait for the hour to reset or increase limit

3. **Verify AI Provider:**
   - Go to Settings → Voice Assistants → Conversation
   - Ensure an AI provider is configured (OpenAI, Google, etc.)

### AI Responses Are Generic

**Problem:** AI analysis doesn't provide specific solutions.

**Solutions:**
1. Use a more capable AI model (GPT-4 vs GPT-3.5)
2. Ensure the log message has enough context
3. Try manual analysis with `use_ai: true`

### AI API Errors

**Problem:** Errors when calling AI service.

**Check:**
- API key validity
- API quota/limits
- Network connectivity
- Service status

## Performance Issues

### High CPU Usage

**Problem:** Home Assistant CPU usage increased after installing.

**Solutions:**

1. **Increase Scan Interval:**
   ```yaml
   # Settings → Devices & Services → Log Debugger → Configure
   # Set scan_interval to 60 or 120 seconds
   ```

2. **Exclude Verbose Integrations:**
   ```yaml
   # Add frequently logging integrations to excluded_integrations
   excluded_integrations: "recorder,logger,zha"
   ```

3. **Disable Auto-Analysis:**
   - Turn off auto_analyze
   - Use manual analysis only when needed

### High Memory Usage

**Problem:** Home Assistant memory usage increased.

**Explanation:**
The integration keeps up to 1000 log entries in memory.

**Solutions:**
1. Clear history periodically:
   ```yaml
   service: ha_log_debugger.clear_analyzed_logs
   ```

2. Create automation to clear daily:
   ```yaml
   automation:
     - alias: "Clear Log History Daily"
       trigger:
         - platform: time
           at: "03:00:00"
       action:
         - service: ha_log_debugger.clear_analyzed_logs
   ```

### Slow Log File Scans

**Problem:** Log scans take a long time.

**Solutions:**
1. Rotate log files more frequently
2. Increase scan interval
3. Exclude verbose integrations

## Sensor Issues

### Sensors Not Updating

**Problem:** Sensor values don't change.

**Solutions:**

1. **Force Update:**
   ```yaml
   service: homeassistant.update_entity
   target:
     entity_id: sensor.log_debugger_errors
   ```

2. **Check Integration Status:**
   - Settings → Devices & Services → Log Debugger
   - Should show "Loaded" not "Failed"

3. **Restart Integration:**
   - Settings → Devices & Services → Log Debugger
   - Click three dots → Reload

### Last Error Sensor Shows "No recent errors"

**Problem:** You know there are errors but sensor shows none.

**Check:**
1. Log level filter might be excluding them
2. Integration might be excluded
3. Errors might be older than the buffer

**Solution:**
- Trigger `scan_logs_now` service
- Lower log level filter
- Check `sensor.log_debugger_total_log_entries`

### Sensor Attributes Empty

**Problem:** Sensor state exists but attributes are empty.

**Likely Cause:** Log parser couldn't extract details.

**Solutions:**
1. Check the actual log format matches expected format
2. Report the log line format as an issue on GitHub

## Service Issues

### Service Call Fails

**Problem:** Calling a service returns an error.

**Common Issues:**

1. **analyze_log_entry:**
   ```yaml
   # Wrong - missing entry_id
   service: ha_log_debugger.analyze_log_entry
   
   # Correct
   service: ha_log_debugger.analyze_log_entry
   data:
     entry_id: "1696723200.0_1234"
   ```

2. **Service Not Found:**
   - Integration might not be loaded
   - Restart Home Assistant

### Services Don't Appear in Developer Tools

**Problem:** Services don't show in Developer Tools → Services.

**Solutions:**
1. Restart Home Assistant
2. Reload integration
3. Check `services.yaml` exists and is valid

## Getting Help

If you're still experiencing issues:

### Before Asking for Help

1. **Check Logs:**
   - Configuration → Logs
   - Filter by "ha_log_debugger"

2. **Enable Debug Logging:**
   ```yaml
   # configuration.yaml
   logger:
     default: info
     logs:
       custom_components.ha_log_debugger: debug
   ```

3. **Gather Information:**
   - Home Assistant version
   - Integration version
   - Relevant log entries
   - Configuration (sanitized)

### Where to Get Help

1. **GitHub Issues:** [Report Bug](https://github.com/loryanstrant/HA-Log-Debugger/issues)
2. **GitHub Discussions:** [Ask Question](https://github.com/loryanstrant/HA-Log-Debugger/discussions)
3. **Home Assistant Community:** [Forum](https://community.home-assistant.io/)

### What to Include

```markdown
**Home Assistant Version:** 2023.x.x
**Integration Version:** 1.0.0
**Issue Description:** Clear description of the problem

**Configuration:**
```yaml
# Your sanitized configuration
```

**Logs:**
```
# Relevant log entries with debug enabled
```

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...
```

## Common Error Messages

### "Log file not found"

**Solution:** Verify log file exists at `/config/home-assistant.log`

### "Unable to perform AI analysis"

**Solution:** Set up Conversation integration with an AI provider

### "Integration failed to set up"

**Solution:** Check Home Assistant logs for specific error, often a dependency issue

### "Maximum retries exceeded"

**Solution:** AI service might be down or rate-limited, try again later

---

**Still need help?** Open an issue on [GitHub](https://github.com/loryanstrant/HA-Log-Debugger/issues) with detailed information.
