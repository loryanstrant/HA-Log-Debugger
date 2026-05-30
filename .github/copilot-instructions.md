# Copilot instructions — HA-Log-Debugger

> Canonical standards live in the `dev-standards` repo on SOUNDWAVE/Gitea.
> Read by Copilot chat **and** inline suggestions. For full HA build conventions,
> see the `build-ha-component` skill in dev-standards.

## What this repo is

A **Home Assistant custom component** that monitors and parses HA logs and
surfaces issues as sensors (with optional AI analysis). Domain: `ha_log_debugger`.

## Repo shape

- `custom_components/ha_log_debugger/` — `manifest.json`, `__init__.py`,
  `config_flow.py`, `const.py`, `log_monitor.py`, `parsers.py`, `ai_analyzer.py`,
  `sensor.py`, `services.yaml`, `strings.json`, `translations/`.
- `hacs.json`, `info.md`, docs (`AUTOMATIONS.md`, `DASHBOARD.md`,
  `TROUBLESHOOTING.md`, `PROJECT_SUMMARY.md`), `.github/workflows/`.

## Conventions

- Bump `manifest.json` **version** every release (semver); `domain` matches the
  folder name.
- Test: `hassfest` + HACS validation, then `pytest` with
  `pytest-homeassistant-custom-component`.
- Deploy/test via the published release artifact into TEST1/TEST2, not host
  file-copy. Backup + auto-rollback.
- If AI analysis uses an external API, that key is user config — never commit it.
- Sibling project `HA-Log-Debugger-AI` is a **separate Dockerised web app**, not
  part of this component.

## Never

- Don't commit HA long-lived tokens, AI API keys, or deploy keys — Gitea Actions
  secrets only.
