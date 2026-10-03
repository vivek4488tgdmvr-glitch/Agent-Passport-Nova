"""Day 30: final local cybersecurity audit."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_passport.security.audit import run_security_audit



def main() -> int:
    report = run_security_audit(ROOT)
    print("=== DAY 30: FINAL CYBERSECURITY AUDIT ===")
    for check in report.checks:
        print(f"{'✓' if check.passed else '✗'} {check.name}: {check.detail}")
    print(f"\nSECURITY AUDIT: {report.passed}/{report.total} checks passed — {report.status}")
    out = ROOT / "security-audit-report.json"
    out.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    print(f"Report: {out.name}")
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
