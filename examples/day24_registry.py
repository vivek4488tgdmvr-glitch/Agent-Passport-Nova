from __future__ import annotations

import json
import tempfile
from pathlib import Path

from agent_passport.passport.signing import generate_keypair, sign_passport
from agent_passport.registry import PassportRegistry


def main() -> None:
    private, public = generate_keypair()
    passport = {
        "passport": {"version": "1.5"},
        "agent": {"id": "nova", "name": "Nova", "version": "1.2.0"},
        "identity": {"capabilities": ["reasoning", "web_search"]},
    }
    signed = sign_passport(passport, private, "demo-issuer")

    with tempfile.TemporaryDirectory() as td:
        registry = PassportRegistry(Path(td) / "registry.json")
        entry = registry.publish(signed, public_key=public)
        retrieved = registry.retrieve_verified(entry.passport_id)
        print("=== DAY 24: PRODUCTION-STYLE REGISTRY ===")
        print(f"Published: {entry.passport_id} ✓")
        print(f"Versions: {registry.versions('nova')}")
        print(f"Latest: {registry.latest('nova').version} ✓")
        print(f"Signed retrieval: {retrieved['status']} ✓")
        registry.revoke(entry.passport_id)
        print(f"Revocation: {registry.verify_registered(entry.passport_id)['status']} ✓")
        print("REGISTRY TRUST PIPELINE ✓")
        print(json.dumps({"status": "PASS", "passport_id": entry.passport_id}, indent=2))


if __name__ == "__main__":
    main()
