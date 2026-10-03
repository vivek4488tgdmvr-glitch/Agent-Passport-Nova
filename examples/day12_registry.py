import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import tempfile
from pathlib import Path

from agent_passport.passport.loader import load
from agent_passport.registry import PassportRegistry


with tempfile.TemporaryDirectory() as td:
    registry = PassportRegistry(Path(td) / "registry.json")
    passport = load("passport.yaml").model_dump(mode="json")

    print("=== DAY 12: PASSPORT REGISTRY ===")
    entry = registry.register(passport, issuer="demo-issuer")
    print("Registered:", entry.passport_id)
    print("Agent:", entry.agent_id, "v" + entry.version)
    print("Fingerprint:", entry.fingerprint[:24] + "...")

    print("\nRegistry lookup:")
    for item in registry.list():
        print(f"  ✓ {item.agent_id} v{item.version} [{item.status.value}]")

    result = registry.verify_registered(entry.passport_id)
    print("\nVerification:", result["status"], "✓")

    registry.revoke(entry.passport_id)
    result = registry.verify_registered(entry.passport_id)
    print("After revocation:", result["status"], "✓" if result["status"] == "FAIL" else "✗")
