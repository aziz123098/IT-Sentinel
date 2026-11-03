# IT Sentinel — Architecture

## Components

- `dashboard.py` — Streamlit user interface for system health, diagnostic results, incident management and report download.
- `advanced_diagnostics.py` — read-only macOS network configuration and system diagnostics.
- `incident_engine.py` — rule-based interpretation of diagnostic signals and suggested troubleshooting steps.
- `incident_database.py` — SQLite persistence of incident records and status.
- `main.py` — command-line diagnostics and JSON report generation.
- `sentinel/checks.py` — earlier diagnostic checks retained for reference.

## Workflow

1. Collect CPU, memory, disk, DNS and TCP connectivity signals.
2. Inspect local network configuration where supported.
3. Apply troubleshooting rules; present potential causes rather than confirmed root causes.
4. Record incidents in SQLite and allow manual status changes.
5. Export a JSON report for review.

## Scope

Local, single-device prototype. No AI model, automatic repair or enterprise fleet monitoring. Do not commit local incident databases or sensitive network reports.
