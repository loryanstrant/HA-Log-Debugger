# Example Automations

This file contains example automations for the Home Assistant Log Debugger integration.

## Basic Notification Automations

### Alert on Critical Errors

```yaml
automation:
  - alias: "Alert on Critical Errors"
    description: "Send a notification when a critical error is detected"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_critical_errors
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚨 Critical Error in Home Assistant"
          message: |
            Component: {{ state_attr('sensor.log_debugger_last_error', 'component') }}
            
            {{ state_attr('sensor.log_debugger_last_error', 'full_message')[:200] }}
          data:
            priority: high
            ttl: 0
            channel: critical_errors
```

### Daily Error Summary

```yaml
automation:
  - alias: "Daily Error Summary"
    description: "Send a daily summary of errors and warnings"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: or
        conditions:
          - condition: numeric_state
            entity_id: sensor.log_debugger_errors
            above: 0
          - condition: numeric_state
            entity_id: sensor.log_debugger_warnings
            above: 5
    action:
      - service: notify.persistent_notification
        data:
          title: "Daily Log Summary"
          message: |
            📊 Today's Log Statistics:
            
            - Warnings: {{ states('sensor.log_debugger_warnings') }}
            - Errors: {{ states('sensor.log_debugger_errors') }}
            - Critical: {{ states('sensor.log_debugger_critical_errors') }}
            
            Last Error: {{ states('sensor.log_debugger_last_error')[:100] }}
```

## AI Analysis Automations

### Auto-Analyze Errors During Off-Peak Hours

```yaml
automation:
  - alias: "Auto-Analyze Errors at Night"
    description: "Automatically analyze errors with AI during off-peak hours"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_errors
    condition:
      - condition: time
        after: "22:00:00"
        before: "06:00:00"
      - condition: numeric_state
        entity_id: sensor.log_debugger_ai_analysis_remaining
        above: 0
      - condition: template
        value_template: >
          {{ trigger.to_state.state | int > trigger.from_state.state | int }}
    action:
      - delay:
          seconds: 5
      - service: ha_log_debugger.analyze_log_entry
        data:
          entry_id: "{{ state_attr('sensor.log_debugger_last_error', 'entry_id') }}"
          use_ai: true
```

### Analyze Only Critical Errors with AI

```yaml
automation:
  - alias: "AI Analyze Critical Errors Only"
    description: "Use AI analysis only for critical errors to save quota"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_critical_errors
    condition:
      - condition: template
        value_template: >
          {{ trigger.to_state.state | int > trigger.from_state.state | int }}
      - condition: numeric_state
        entity_id: sensor.log_debugger_ai_analysis_remaining
        above: 0
    action:
      - service: ha_log_debugger.analyze_log_entry
        data:
          entry_id: "{{ state_attr('sensor.log_debugger_last_error', 'entry_id') }}"
          use_ai: true
      - service: notify.mobile_app_your_phone
        data:
          title: "Critical Error Analyzed"
          message: |
            {{ state_attr('sensor.log_debugger_last_error', 'ai_analysis') }}
```

## Maintenance Automations

### Clear Log History Weekly

```yaml
automation:
  - alias: "Clear Log History Weekly"
    description: "Clear analyzed log history every Sunday"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: ha_log_debugger.clear_analyzed_logs
      - service: notify.persistent_notification
        data:
          title: "Log Debugger"
          message: "Log history cleared"
```

### Periodic Manual Scan

```yaml
automation:
  - alias: "Scan Logs Every 5 Minutes"
    description: "Manually trigger log scan more frequently"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    action:
      - service: ha_log_debugger.scan_logs_now
```

## Advanced Automations

### Integration-Specific Error Handling

```yaml
automation:
  - alias: "Handle ZHA Errors"
    description: "Special handling for ZHA integration errors"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_last_error
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.log_debugger_last_error', 'component') == 'zha' }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "ZHA Error Detected"
          message: |
            A ZHA error occurred. Consider:
            1. Checking Zigbee coordinator connectivity
            2. Reviewing device signal strength
            3. Restarting the ZHA integration
            
            Error: {{ states('sensor.log_debugger_last_error')[:150] }}
      - service: ha_log_debugger.analyze_log_entry
        data:
          entry_id: "{{ state_attr('sensor.log_debugger_last_error', 'entry_id') }}"
          use_ai: true
```

### Template Error Auto-Fix Notification

```yaml
automation:
  - alias: "Template Error Notification"
    description: "Notify with suggested fix for template errors"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_last_error
    condition:
      - condition: template
        value_template: >
          {{ 'template' in states('sensor.log_debugger_last_error') | lower }}
    action:
      - service: persistent_notification.create
        data:
          title: "Template Error Detected"
          message: |
            **Error:**
            {{ states('sensor.log_debugger_last_error')[:200] }}
            
            **Affected Entity:**
            {{ state_attr('sensor.log_debugger_last_error', 'entity_id') }}
            
            **Suggested Fix:**
            {{ state_attr('sensor.log_debugger_last_error', 'suggested_fix') }}
            
            [Test Template in Developer Tools](/developer-tools/template)
          notification_id: template_error
```

### Error Threshold Alert

```yaml
automation:
  - alias: "Too Many Errors Alert"
    description: "Alert when error count exceeds threshold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.log_debugger_errors
        above: 10
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ High Error Count"
          message: |
            Home Assistant has logged {{ states('sensor.log_debugger_errors') }} errors.
            
            This may indicate a systemic issue that needs attention.
            
            Last error: {{ states('sensor.log_debugger_last_error')[:100] }}
          data:
            priority: high
      - service: ha_log_debugger.scan_logs_now
```

### AI Quota Management

```yaml
automation:
  - alias: "AI Quota Low Alert"
    description: "Notify when AI analysis quota is running low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.log_debugger_ai_analysis_remaining
        below: 3
    action:
      - service: notify.persistent_notification
        data:
          title: "Log Debugger - AI Quota Low"
          message: |
            Only {{ states('sensor.log_debugger_ai_analysis_remaining') }} AI analyses remaining this hour.
            
            Consider:
            - Disabling auto-analyze temporarily
            - Increasing the hourly limit
            - Waiting for the quota to reset
```

### Entity-Specific Error Tracking

```yaml
automation:
  - alias: "Track Errors by Entity"
    description: "Create input_text tracker for problem entities"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_last_error
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.log_debugger_last_error', 'entity_id') is not none }}
    action:
      - service: input_text.set_value
        target:
          entity_id: input_text.last_error_entity
        data:
          value: "{{ state_attr('sensor.log_debugger_last_error', 'entity_id') }}"
      - service: counter.increment
        target:
          entity_id: counter.errors_for_{{ state_attr('sensor.log_debugger_last_error', 'entity_id') | replace('.', '_') }}
```

## Script Examples

### Manual Error Investigation Script

```yaml
script:
  investigate_last_error:
    alias: "Investigate Last Error"
    description: "Trigger AI analysis and send detailed notification"
    sequence:
      - service: ha_log_debugger.analyze_log_entry
        data:
          entry_id: "{{ state_attr('sensor.log_debugger_last_error', 'entry_id') }}"
          use_ai: true
      - delay:
          seconds: 10
      - service: notify.mobile_app_your_phone
        data:
          title: "Error Investigation Results"
          message: |
            **Component:** {{ state_attr('sensor.log_debugger_last_error', 'component') }}
            
            **Error:** {{ states('sensor.log_debugger_last_error')[:150] }}
            
            **AI Analysis:**
            {{ state_attr('sensor.log_debugger_last_error', 'ai_analysis')[:500] }}
            
            **Suggested Fix:**
            {{ state_attr('sensor.log_debugger_last_error', 'suggested_fix')[:300] }}
```

### Batch Clear and Scan

```yaml
script:
  refresh_log_debugger:
    alias: "Refresh Log Debugger"
    description: "Clear history and do a fresh scan"
    sequence:
      - service: ha_log_debugger.clear_analyzed_logs
      - delay:
          seconds: 2
      - service: ha_log_debugger.scan_logs_now
      - service: persistent_notification.create
        data:
          title: "Log Debugger Refreshed"
          message: "Log history cleared and fresh scan completed"
```

## Dashboard Button Examples

### Quick Action Buttons

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Investigate
    icon: mdi:magnify
    tap_action:
      action: call-service
      service: script.investigate_last_error
  - type: button
    name: Scan Now
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: ha_log_debugger.scan_logs_now
  - type: button
    name: Clear
    icon: mdi:delete
    tap_action:
      action: call-service
      service: ha_log_debugger.clear_analyzed_logs
      confirmation:
        text: Clear all log history?
```

## Integration with Other Services

### Send to Discord

```yaml
automation:
  - alias: "Critical Errors to Discord"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_critical_errors
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.discord
        data:
          message: |
            **🚨 Critical Error in Home Assistant**
            
            Component: `{{ state_attr('sensor.log_debugger_last_error', 'component') }}`
            Entity: `{{ state_attr('sensor.log_debugger_last_error', 'entity_id') }}`
            
            Error:
            ```
            {{ states('sensor.log_debugger_last_error')[:500] }}
            ```
```

### Create GitHub Issue Automatically

```yaml
automation:
  - alias: "Create GitHub Issue for Repeated Errors"
    description: "Create a GitHub issue if the same error occurs multiple times"
    trigger:
      - platform: state
        entity_id: sensor.log_debugger_errors
        for:
          minutes: 5
    condition:
      - condition: numeric_state
        entity_id: sensor.log_debugger_errors
        above: 5
    action:
      - service: shell_command.create_github_issue
        data:
          title: "Repeated Error: {{ state_attr('sensor.log_debugger_last_error', 'component') }}"
          body: |
            Auto-generated from Home Assistant Log Debugger
            
            Error occurred 5+ times in 5 minutes
            
            {{ state_attr('sensor.log_debugger_last_error', 'full_message') }}
            
            AI Analysis:
            {{ state_attr('sensor.log_debugger_last_error', 'ai_analysis') }}
```

Note: For the GitHub issue creation, you'd need to set up a shell command with the GitHub CLI.
