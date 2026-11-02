# 🛡️ IT Sentinel — Smart IT Diagnostics & Incident Management

**A local, read-only macOS IT troubleshooting dashboard built with Python, Streamlit, psutil, and SQLite.**

IT Sentinel checks DNS resolution, external TCP connectivity, CPU, memory, and disk usage, then presents rule-based troubleshooting recommendations and an incident history.

## Features
- System health overview and resource utilization
- DNS and TCP connectivity diagnostics
- macOS network configuration inspection: DNS resolvers, default gateway, route interface
- Rule-based network troubleshooting and suggested next steps
- SQLite incident logging and manual incident closure
- Safe, synthetic DNS failure simulation
- JSON report download

## Dashboard screenshots
Screenshots are from an **earlier working version**, not the latest enhanced release. Updated screenshots will be added after the enhanced dashboard is verified on a Mac.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
streamlit run dashboard.py
```

Open http://localhost:8501.

## Project structure
- `main.py`: runs diagnostics and writes the latest JSON report
- `advanced_diagnostics.py`: read-only checks and network configuration inspection
- `dashboard.py`: Streamlit user interface
- `incident_engine.py`: rule-based incident explanations
- `incident_database.py`: SQLite incident records
- `sentinel/checks.py`: earlier checks module

## Important limitations
This is a **single-device prototype**, not an enterprise monitoring product. Diagnoses are hypotheses, not proven root causes. It does **not** use an AI model, execute automatic repairs, or monitor multiple devices. A successful DNS/TCP test does not guarantee full internet access.

## Privacy
Do not commit `incidents.db`, `reports/latest.json`, credentials, or machine-specific network information. Review any exported reports before sharing.

## Author
Abdulaziz Aali — Computer Science | IT Infrastructure & Technical Support
