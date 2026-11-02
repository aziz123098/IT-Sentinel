import json
from pathlib import Path
from advanced_diagnostics import run_diagnostics

def main():
    report = run_diagnostics()
    for item in report["results"]:
        print(f"[{item['status']}] {item['check']}: {item['detail']}")
    output = Path(__file__).resolve().parent / "reports" / "latest.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved: {output}")

if __name__ == "__main__":
    main()
