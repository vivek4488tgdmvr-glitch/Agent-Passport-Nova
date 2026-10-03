from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_threat_model_exists_and_covers_required_sections():
    text = (ROOT / "SECURITY_THREAT_MODEL.md").read_text(encoding="utf-8")
    for heading in ["## Assets", "## Threats and mitigations", "## Security decision flow", "## Security claims we do not make"]:
        assert heading in text
    for threat in ["T1 — Forged Passport", "T2 — Delegation replay", "T3 — Privilege escalation", "T4 — Malicious tool execution", "T5 — Credential leakage", "T6 — Audit tampering", "T7 — Request flooding", "T8 — Registry substitution/revocation bypass"]:
        assert threat in text


def test_security_control_matrix_maps_controls_to_verification():
    text = (ROOT / "SECURITY_CONTROL_MATRIX.md").read_text(encoding="utf-8")
    required = [
        "Passport signature", "Capability negotiation", "Permission policy",
        "Delegation scope", "Replay guard", "Rate limiter", "Secret redaction",
        "Audit chain", "Sandbox", "Encrypted keystore", "Registry verification", "Red-team suite",
    ]
    assert all(item in text for item in required)
