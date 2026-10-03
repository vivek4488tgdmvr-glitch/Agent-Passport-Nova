from pathlib import Path
import json

from agent_passport.passport import export_passport, fingerprint, load, verify

source = Path("passport.yaml")
json_output = Path("passport-export.json")

passport = load(source)

print("=== PASSPORT LOADED ===")
print(f"Agent: {passport.agent.name} v{passport.agent.version}")

print("\n=== FINGERPRINT ===")
print(fingerprint(passport))

print("\n=== VERIFICATION REPORT ===")
print(json.dumps(verify(source), indent=2))

print("\n=== EXPORT ===")
export_passport(passport, json_output)
print(f"Created {json_output}")

json_output.unlink(missing_ok=True)
