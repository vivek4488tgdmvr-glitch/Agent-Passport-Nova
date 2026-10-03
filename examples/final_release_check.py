"""Agent Passport Day 30 hardened final release verification.

Runs the release-grade checks used for the competition submission and writes
an auditable final-release-report.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, args: list[str]) -> dict:
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(ROOT) + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, env=env)
    return {
        "name": label,
        "command": " ".join(args),
        "returncode": p.returncode,
        "status": "PASS" if p.returncode == 0 else "FAIL",
        "stdout": p.stdout[-4000:],
        "stderr": p.stderr[-2000:],
    }


def main() -> int:
    checks = [
        run("full test suite", [sys.executable, "-m", "pytest", "-q"]),
        run("passport travel", [sys.executable, "examples/day20_passport_travel.py"]),
        run("cryptographic evidence", [sys.executable, "examples/day22_evidence.py"]),
        run("advanced security", [sys.executable, "examples/day23_advanced_security.py"]),
        run("production registry", [sys.executable, "examples/day24_registry.py"]),
        run("secure key management", [sys.executable, "examples/day27_key_management.py"]),
        run("safe red-team suite", [sys.executable, "examples/day29_red_team.py"]),
        run("final cybersecurity audit", [sys.executable, "examples/day30_security_audit.py"]),
    ]
    report = {
        "release": "Agent Passport Day 30 — Hardened Security Release",
        "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
        "checks": checks,
        "artifacts": [
            "passport.yaml",
            "passport-travel-evidence.json",
            "passport-travel-evidence-signed.json",
            "SUBMISSION_CHECKLIST.md",
            "SECURITY_AUDIT.md",
            "security-audit-report.json",
        ],
    }
    (ROOT / "final-release-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("=== AGENT PASSPORT DAY 30 HARDENED SECURITY RELEASE ===")
    for check in checks:
        print(f"{check['status']}: {check['name']}")
    print(f"FINAL RELEASE: {report['status']}")
    print("Report: final-release-report.json")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
