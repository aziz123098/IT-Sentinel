"""Read-only diagnostics for the local macOS workstation."""
import json
import platform
import re
import socket
import subprocess
from datetime import datetime, timezone
import psutil

def command_output(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=8, check=False)
        return result.stdout if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""

def inspect_network_configuration():
    if platform.system() != "Darwin":
        return {"gateway": None, "interface": None, "dns_servers": [], "note": "Network configuration inspection currently supports macOS."}
    route = command_output(["route", "-n", "get", "default"])
    dns = command_output(["scutil", "--dns"])
    gateway = re.search(r"^\s*gateway:\s*(\S+)", route, re.M)
    interface = re.search(r"^\s*interface:\s*(\S+)", route, re.M)
    primary = dns.split("resolver #1", 1)[-1].split("resolver #2", 1)[0] if "resolver #1" in dns else ""
    servers = re.findall(r"nameserver\[\d+\]\s*:\s*(\S+)", primary)
    return {
        "gateway": gateway.group(1) if gateway else None,
        "interface": interface.group(1) if interface else None,
        "dns_servers": list(dict.fromkeys(servers)),
        "note": "Configuration detected; gateway reachability is not independently verified."
    }

def check_dns():
    try:
        address = socket.gethostbyname("example.com")
        return {"check": "DNS", "status": "PASS", "detail": f"example.com resolved to {address}"}
    except OSError as error:
        return {"check": "DNS", "status": "FAIL", "detail": str(error)}

def check_network():
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=4):
            return {"check": "TCP connectivity", "status": "PASS", "detail": "Connected to 1.1.1.1:443"}
    except OSError as error:
        return {"check": "TCP connectivity", "status": "FAIL", "detail": str(error)}

def check_resources():
    usages = {
        "CPU": psutil.cpu_percent(interval=0.5),
        "Memory": psutil.virtual_memory().percent,
        "Disk": psutil.disk_usage("/").percent,
    }
    return [
        {"check": name, "status": "WARN" if value >= (90 if name == "Disk" else 85) else "PASS", "detail": f"Usage: {value:.1f}%"}
        for name, value in usages.items()
    ]

def diagnose_network(results):
    statuses = {r.get("check"): r.get("status") for r in results}
    dns, tcp = statuses.get("DNS"), statuses.get("TCP connectivity")
    if dns == "FAIL" and tcp == "PASS":
        return {"problem": "Possible DNS issue", "severity": "High", "reason": "DNS lookup failed, while a direct TCP test succeeded.", "recommendation": "Review DNS settings and test resolution with a different resolver."}
    if dns == "FAIL" and tcp == "FAIL":
        return {"problem": "Possible broader connectivity issue", "severity": "High", "reason": "DNS lookup and the external TCP test both failed.", "recommendation": "Check network connection, gateway, firewall, and test another endpoint."}
    if dns == "PASS" and tcp == "FAIL":
        return {"problem": "Possible TCP path or endpoint issue", "severity": "Warning", "reason": "DNS lookup succeeded, but TCP to the tested endpoint failed.", "recommendation": "Check endpoint availability, routing, and network restrictions."}
    if dns == "PASS" and tcp == "PASS":
        return {"problem": "No network issue detected by these tests", "severity": "None", "reason": "DNS lookup and one external TCP connection succeeded.", "recommendation": "No immediate action indicated by these two tests."}
    return {"problem": "Insufficient data", "severity": "Unknown", "reason": "Required test results are missing.", "recommendation": "Run diagnostics again."}

def run_diagnostics():
    results = [check_dns(), check_network(), *check_resources()]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device": platform.node(),
        "os": platform.platform(),
        "results": results,
        "network_configuration": inspect_network_configuration(),
        "network_diagnosis": diagnose_network(results),
    }

if __name__ == "__main__":
    print(json.dumps(run_diagnostics(), indent=2))
