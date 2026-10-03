import json
from pathlib import Path

from agent_passport.security.redteam import run_red_team_suite


report = run_red_team_suite()
print("\n=== DAY 29: SAFE RED-TEAM SECURITY TEST ===\n")
print(report.pretty())
Path("red-team-report.json").write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
print("\nEvidence: red-team-report.json")
