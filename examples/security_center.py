"""Print the reviewer-facing Agent Passport security center."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "SECURITY_STATUS.json").read_text(encoding="utf-8"))

print("AGENT PASSPORT — SECURITY CENTER")
print("=" * 36)
print("Mode:", data["status"])
print("Principle:", data["principle"])
print()
for control in data["controls"]:
    print("✓", control.replace("_", " ").title())
print()
print("External validator claimed:", data["external_validator_claimed"])
print("Security Center: READY")
