"""Day 22: cryptographically signed Passport Travel evidence."""

import json
from pathlib import Path

from agent_passport.passport.evidence import sign_evidence, verify_evidence
from agent_passport.passport.fingerprint import fingerprint
from agent_passport.passport.loader import load
from agent_passport.passport.signing import generate_keypair
from agent_passport.travel import run_travel_demo

ROOT = Path(__file__).resolve().parents[1]


def main():
    passport = load(ROOT / "passport.yaml")
    passport_fp = fingerprint(passport)
    travel = run_travel_demo().to_dict()
    private, _ = generate_keypair()
    signed = sign_evidence(travel, passport_fp, private, "demo-issuer")
    out = ROOT / "passport-travel-evidence-signed.json"
    out.write_text(json.dumps(signed, indent=2) + "\n", encoding="utf-8")
    result = verify_evidence(signed, passport_fp)

    tampered = json.loads(json.dumps(signed))
    tampered["steps"][0]["detail"] = "TAMPERED"
    tampered_result = verify_evidence(tampered, passport_fp)

    print("=== DAY 22: CRYPTOGRAPHIC EVIDENCE ===")
    print(f"Passport fingerprint: {passport_fp}")
    print(f"Evidence hash: {signed['cryptographic_evidence']['evidence_sha256']}")
    print(f"Signed evidence: {result['status']} ✓")
    print(f"Tamper detection: {tampered_result['status'] == 'FAIL'} ✓")
    print(f"Evidence file: {out.name}")
    print("CRYPTOGRAPHIC EVIDENCE ✓")


if __name__ == "__main__":
    main()
