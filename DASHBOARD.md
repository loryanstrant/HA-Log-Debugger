# Example Dashboard Configuration

This document provides example Lovelace dashboard cards for the Log Debugger integration.

## Basic Statistics Card

```yaml
type: entities
title: Log Debugger Statistics
entities:
  - entity: sensor.log_debugger_total_log_entries
    name: Total Entries
  - entity: sensor.log_debugger_warnings
    name: Warnings
  - entity: sensor.log_debugger_errors
    name: Errors
  - entity: sensor.log_debugger_critical_errors
    name: Critical
  - entity: sensor.log_debugger_ai_analysis_remaining
    name: AI Calls Remaining
```

## Detailed Last Error Card

```yaml
type: markdown
content: >
  ## Last Error

  **Level:** {{ state_attr('sensor.log_debugger_last_error', 'level') }}

  **Component:** {{ state_attr('sensor.log_debugger_last_error', 'component') }}

  **Time:** {{ state_attr('sensor.log_debugger_last_error', 'timestamp') | as_timestamp | timestamp_custom('%Y-%m-%d %H:%M:%S') }}

  **Message:** {{ state_attr('sensor.log_debugger_last_error', 'full_message') }}

  {% if state_attr('sensor.log_debugger_last_error', 'entity_id') %}
  **Entity:** `{{ state_attr('sensor.log_debugger_last_error', 'entity_id') }}`
  {% endif %}

  {% if state_attr('sensor.log_debugger_last_error', 'ai_analysis') %}
  ### AI Analysis
  {{ state_attr('sensor.log_debugger_last_error', 'ai_analysis') }}
  {% endif %}

  {% if state_attr('sensor.log_debugger_last_error', 'suggested_fix') %}
  ### Suggested Fix
  ```yaml
  {{ state_attr('sensor.log_debugger_last_error', 'suggested_fix') }}
  ```
  {% endif %}
title: null
```

## Error Trend Graph

```yaml
type: history-graph
title: Error Trends
hours_to_show: 24
entities:
  - entity: sensor.log_debugger_warnings
    name: Warnings
  - entity: sensor.log_debugger_errors
    name: Errors
  - entity: sensor.log_debugger_critical_errors
    name: Critical
```

## Quick Actions Card

```yaml
type: button
name: Scan Logs Now
icon: mdi:magnify-scan
tap_action:
  action: call-service
  service: ha_log_debugger.scan_logs_now
```

```yaml
type: button
name: Clear History
icon: mdi:delete-sweep
tap_action:
  action: call-service
  service: ha_log_debugger.clear_analyzed_logs
  confirmation:
    text: Are you sure you want to clear all log history?
```

## Combined Dashboard View

```yaml
title: Log Debugger
path: log-debugger
icon: mdi:bug
badges: []
cards:
  - type: horizontal-stack
    cards:
      - type: statistic
        entity: sensor.log_debugger_warnings
        name: Warnings
        icon: mdi:alert
      - type: statistic
        entity: sensor.log_debugger_errors
        name: Errors
        icon: mdi:alert-circle
      - type: statistic
        entity: sensor.log_debugger_critical_errors
        name: Critical
        icon: mdi:alert-octagon
  
  - type: history-graph
    title: Error Trends (24h)
    hours_to_show: 24
    entities:
      - sensor.log_debugger_warnings
      - sensor.log_debugger_errors
      - sensor.log_debugger_critical_errors
  
  - type: markdown
    content: >
      ## Last Error

      **Level:** {{ state_attr('sensor.log_debugger_last_error', 'level') }}

      **Component:** {{ state_attr('sensor.log_debugger_last_error', 'component') }}

      **Time:** {{ state_attr('sensor.log_debugger_last_error', 'timestamp') | as_timestamp | timestamp_custom('%Y-%m-%d %H:%M:%S') }}

      **Message:** {{ state_attr('sensor.log_debugger_last_error', 'full_message')[:200] }}...

      {% if state_attr('sensor.log_debugger_last_error', 'entity_id') %}
      **Entity:** `{{ state_attr('sensor.log_debugger_last_error', 'entity_id') }}`
      {% endif %}

      {% if state_attr('sensor.log_debugger_last_error', 'github_url') %}
      [View Documentation]({{ state_attr('sensor.log_debugger_last_error', 'github_url') }})
      {% endif %}
    title: Latest Issue
  
  - type: entities
    title: AI Analysis Status
    entities:
      - entity: sensor.log_debugger_ai_analysis_remaining
        name: Analyses Remaining
        secondary_info: last-changed
  
  - type: horizontal-stack
    cards:
      - type: button
        name: Scan Now
        icon: mdi:magnify-scan
        tap_action:
          action: call-service
          service: ha_log_debugger.scan_logs_now
      - type: button
        name: Clear History
        icon: mdi:delete-sweep
        tap_action:
          action: call-service
          service: ha_log_debugger.clear_analyzed_logs
          confirmation:
            text: Clear all analyzed logs?
```

## Conditional Card (Only Show When Errors Exist)

```yaml
type: conditional
conditions:
  - condition: numeric_state
    entity: sensor.log_debugger_errors
    above: 0
card:
  type: markdown
  content: >
    ## ⚠️ Active Errors Detected

    You have **{{ states('sensor.log_debugger_errors') }}** errors in your logs.

    {{ state_attr('sensor.log_debugger_last_error', 'full_message')[:150] }}

    [View Full Details](#)
  title: Alert
```

## Mobile Dashboard Card

```yaml
type: glance
title: Log Status
entities:
  - entity: sensor.log_debugger_errors
    name: Errors
  - entity: sensor.log_debugger_warnings
    name: Warnings
  - entity: sensor.log_debugger_ai_analysis_remaining
    name: AI Left
show_name: true
show_state: true
```
