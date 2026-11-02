import json
from pathlib import Path

REPORT = Path(__file__).resolve().parent / "reports" / "latest.json"

def analyze_incidents(results):
    incidents = []
    for result in results:
        name = result.get("check", "")
        status = result.get("status", "UNKNOWN")
        detail = result.get("detail", "")
        if status == "PASS":
            continue
        incident = {
            "check": name, "status": status, "detail": detail,
            "severity": "Warning" if status == "WARN" else "High",
            "causes": [], "recommendations": []
        }
        if name == "DNS":
            incident["causes"] = ["DNS server unavailable", "Incorrect DNS settings", "Network connectivity problem"]
            incident["recommendations"] = ["Check internet connectivity", "Verify configured DNS servers", "Test DNS resolution with another resolver"]
        elif name == "TCP connectivity":
            incident["causes"] = ["Remote endpoint unavailable", "Firewall or network restrictions", "Routing or connectivity problem"]
            incident["recommendations"] = ["Verify network connection", "Check the target host and port", "Review firewall and network restrictions"]
        elif name in ["CPU", "Memory", "Disk"]:
            incident["causes"] = ["High resource utilization", "Background applications or processes", "Insufficient available resources"]
            incident["recommendations"] = ["Inspect resource usage in Activity Monitor", "Identify resource-intensive processes", "Review running applications and storage"]
        else:
            incident["causes"] = ["Cause not yet identified"]
            incident["recommendations"] = ["Review the diagnostic details manually"]
        incidents.append(incident)
    return incidents

if __name__ == "__main__":
    with open(REPORT, encoding="utf-8") as file:
        report = json.load(file)
    incidents = analyze_incidents(report.get("results", []))
    print(f"Detected incidents: {len(incidents)}")
    for incident in incidents:
        print(json.dumps(incident, indent=2))
