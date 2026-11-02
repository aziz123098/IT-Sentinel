import platform
import socket
import shutil
import psutil

def result(name, status, detail):
    return {"check": name, "status": status, "detail": detail}

def run_checks():
    results = []
    try:
        socket.getaddrinfo("example.com", 443)
        results.append(result("DNS", "PASS", "example.com resolved"))
    except OSError as exc:
        results.append(result("DNS", "FAIL", str(exc)))
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=3):
            results.append(result("TCP connectivity", "PASS", "Connected to 1.1.1.1:443"))
    except OSError as exc:
        results.append(result("TCP connectivity", "FAIL", str(exc)))
    cpu = psutil.cpu_percent(interval=0.5)
    results.append(result("CPU", "WARN" if cpu >= 85 else "PASS", f"Usage: {cpu}%"))
    mem = psutil.virtual_memory().percent
    results.append(result("Memory", "WARN" if mem >= 85 else "PASS", f"Usage: {mem}%"))
    disk = shutil.disk_usage("/")
    used = round(disk.used / disk.total * 100, 1)
    results.append(result("Disk", "WARN" if used >= 90 else "PASS", f"Usage: {used}%"))
    return {"device": platform.node(), "os": platform.platform(), "results": results}
