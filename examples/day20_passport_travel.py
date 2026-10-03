import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.travel import run_travel_demo


evidence = run_travel_demo()

print("=== DAY 20: PASSPORT TRAVEL ===")
print()
print(evidence.pretty())

output = Path("passport-travel-evidence.json")
output.write_text(json.dumps(evidence.to_dict(), indent=2), encoding="utf-8")
print(f"\nEvidence file: {output}")
print("\nPASSPORT TRAVEL", "✓" if evidence.status == "PASS" else "✗")
