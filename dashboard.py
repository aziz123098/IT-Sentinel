"""IT Sentinel dashboard. All diagnostics are read-only."""
import json
import subprocess
import sys
from pathlib import Path

import streamlit as st
from advanced_diagnostics import diagnose_network
from incident_database import get_incidents, resolve_incident, save_incident
from incident_engine import analyze_incidents

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "latest.json"
MAIN = ROOT / "main.py"

st.set_page_config(page_title="IT Sentinel | Dashboard", page_icon="🛡️", layout="wide")
st.title("🛡️ IT Sentinel")
st.caption("Local macOS diagnostics • Network troubleshooting • Incident management")
st.divider()

st.subheader("System Health Overview")
left, right = st.columns([3, 1])
with right:
    run = st.button("🔄 Run Full Diagnostics", use_container_width=True)
if run:
    try:
        with st.spinner("Running read-only diagnostics..."):
            proc = subprocess.run([sys.executable, str(MAIN)], cwd=str(ROOT),
                                  capture_output=True, text=True, timeout=45)
        if proc.returncode != 0:
            st.error(proc.stderr or "Diagnostics failed.")
        else:
            new_report = json.loads(REPORT.read_text(encoding="utf-8"))
            current = analyze_incidents(new_report.get("results", []))
            existing = get_incidents()
            open_real = {i["check_name"] for i in existing
                         if i["status"] == "Open" and i["source"] == "Real Scan"}
            for incident in current:
                if incident["check"] not in open_real:
                    save_incident(incident["check"], incident["severity"],
                                  incident["detail"], source="Real Scan")
            st.success("Diagnostics completed. New failures logged without duplicate open incidents.")
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        st.error(f"Diagnostics could not finish: {exc}")

if not REPORT.exists():
    st.info("No report yet. Click Run Full Diagnostics.")
    st.stop()
try:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    st.error(f"Could not read report: {exc}")
    st.stop()

results = report.get("results", [])
passed = sum(i.get("status") == "PASS" for i in results)
failed = sum(i.get("status") == "FAIL" for i in results)
warnings = sum(i.get("status") == "WARN" for i in results)
for col, title, value in zip(st.columns(4),
                             ["Total Checks", "Passed", "Failed", "Warnings"],
                             [len(results), passed, failed, warnings]):
    col.metric(title, value)
st.caption(f"Device: {report.get('device', 'Unknown')} | OS: {report.get('os', 'Unknown')} | Last scan (UTC): {report.get('timestamp', 'Unknown')}")

st.divider()
st.subheader("Hardware Monitoring")
hardware = {}
for item in results:
    if item.get("check") in ("CPU", "Memory", "Disk"):
        try:
            hardware[item["check"]] = float(item.get("detail", "").split("Usage:")[1].replace("%", "").strip())
        except (ValueError, IndexError):
            pass
for col, name in zip(st.columns(3), ("CPU", "Memory", "Disk")):
    with col:
        value = hardware.get(name)
        st.markdown(f"#### {name}")
        if value is None:
            st.info("No data")
        else:
            st.metric("Usage", f"{value:.1f}%")
            st.progress(min(max(value / 100, 0), 1))
st.caption('Disk uses psutil.disk_usage("/") consistently in the CLI and dashboard.')

st.divider()
st.subheader("Diagnostic Results")
for item in results:
    label = f"{item.get('check', 'Unknown')} — {item.get('detail', '')}"
    if item.get("status") == "PASS":
        st.success(f"✅ {label}")
    elif item.get("status") == "WARN":
        st.warning(f"⚠️ {label}")
    else:
        st.error(f"❌ {label}")

st.divider()
st.subheader("🌐 Advanced Network Diagnostics")
config = report.get("network_configuration")
if config:
    c1, c2 = st.columns(2)
    c1.metric("Default Gateway", config.get("gateway") or "Not detected")
    c2.metric("Route Interface", config.get("interface") or "Not detected")
    servers = config.get("dns_servers", [])
    st.write("**Primary DNS resolver servers:**", ", ".join(servers) if servers else "Not detected")
    st.caption(config.get("note", ""))
    st.caption("Configuration does not prove gateway or DNS server availability.")
else:
    st.info("Advanced network configuration not in this report. Click Run Full Diagnostics.")

st.divider()
st.subheader("🧭 Network Troubleshooting")
diagnosis = report.get("network_diagnosis") or diagnose_network(results)
severity = diagnosis.get("severity", "Unknown")
if severity == "None":
    st.success(diagnosis.get("problem", "No issue detected"))
elif severity in ("High", "Critical"):
    st.error(diagnosis.get("problem", "Potential issue"))
else:
    st.warning(diagnosis.get("problem", "Review needed"))
st.write("**Evidence:**", diagnosis.get("reason", ""))
st.write("**Recommended next step:**", diagnosis.get("recommendation", ""))
st.caption("Rule-based hypotheses, not proven root causes. No repairs are executed.")

st.divider()
st.subheader("🚨 Incident Management")
active = analyze_incidents(results)
if not active:
    st.success("No issues detected in the latest scan.")
else:
    st.error(f"{len(active)} issue(s) detected in the latest scan")
    for incident in active:
        with st.expander(f"⚠️ {incident['check']} — {incident['severity']}", expanded=True):
            st.write("**Result:**", incident["status"])
            st.write("**Details:**", incident["detail"])
            st.markdown("**Possible causes**")
            for cause in incident["causes"]:
                st.write(f"• {cause}")
            st.markdown("**Recommended actions**")
            for action in incident["recommendations"]:
                st.write(f"• {action}")

st.divider()
st.subheader("🧪 Incident Simulation Lab")
st.caption("Synthetic DNS failure only. No device settings are changed and no incident is saved automatically.")
if st.button("Simulate DNS Failure"):
    simulated = analyze_incidents([{"check": "DNS", "status": "FAIL",
                                   "detail": "DNS lookup failed (simulation)"}])
    for incident in simulated:
        st.error(f"Simulated {incident['check']} failure — {incident['severity']}")
        st.write("**Possible causes:**", "; ".join(incident["causes"]))
        st.write("**Recommendations:**", "; ".join(incident["recommendations"]))

st.divider()
st.subheader("📋 Incident History")
history = get_incidents()
if history:
    st.dataframe(history, use_container_width=True, hide_index=True)
    open_items = [item for item in history if item["status"] == "Open"]
    if open_items:
        selected = st.selectbox("Select an open incident to close administratively",
                                options=[item["id"] for item in open_items],
                                format_func=lambda item_id: f"Incident #{item_id}")
        if st.button("✅ Mark as Resolved"):
            if resolve_incident(selected):
                st.success(f"Incident #{selected} marked Resolved. This does not repair the device.")
                st.rerun()
            else:
                st.warning("Could not update incident.")
else:
    st.info("No incidents recorded yet.")

st.divider()
st.subheader("📥 Export Report")
st.download_button("Download Latest Report (JSON)",
                   data=json.dumps(report, indent=2, ensure_ascii=False),
                   file_name="it-sentinel-report.json", mime="application/json")
st.caption("Reports may contain device names and private network configuration. Review before sharing.")
