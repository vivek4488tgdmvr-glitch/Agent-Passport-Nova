import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from agent_passport.passport.signing import generate_keypair, sign_passport, verify_signature

passport = {
    "passport": {"version": "1.5"},
    "agent": {
        "id": "nova",
        "name": "Nova",
        "version": "1.0.0",
    },
    "identity": {"capabilities": ["reasoning", "structured_output"]},
}

private, public = generate_keypair()
signed = sign_passport(passport, private, "demo-issuer")

print("=== DAY 11: SIGNED PASSPORT ===")
print("Algorithm:", signed["signature"]["algorithm"])
print("Issuer:", signed["signature"]["issuer"])
print("Content SHA-256:", signed["signature"]["content_sha256"][:24] + "...")

result = verify_signature(signed, public)
print("\nOriginal Passport:", result["status"], "✓" if result["status"] == "PASS" else "✗")

tampered = json.loads(json.dumps(signed))
tampered["agent"]["name"] = "Tampered Nova"
result = verify_signature(tampered, public)
print("Tampered Passport:", result["status"], "✓" if result["status"] == "FAIL" else "✗")
