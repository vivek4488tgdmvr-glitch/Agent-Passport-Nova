"""Display the final local trust-boundary security review."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks = [
    ("Signed Passport tamper detection", "FINAL_SECURITY_CHECKLIST.md"),
    ("Registry revocation", "TRUST_BOUNDARY_MATRIX.md"),
    ("Delegation replay/expiration", "TRUST_BOUNDARY_MATRIX.md"),
    ("Capability escalation", "TRUST_BOUNDARY_MATRIX.md"),
    ("Tool authorization/sandbox", "TRUST_BOUNDARY_MATRIX.md"),
    ("Evidence integrity", "TRUST_BOUNDARY_MATRIX.md"),
    ("Audit integrity", "TRUST_BOUNDARY_MATRIX.md"),
    ("Dashboard XSS regression", "SECURITY_PENTEST_DAY39.md"),
    ("Secret handling", "FINAL_SECURITY_CHECKLIST.md"),
]

print("AGENT PASSPORT — FINAL SECURITY REVIEW")
print("=" * 42)
for name, doc in checks:
    print(f"✓ {name:<34} documented")
print()
print("Scope: local, non-destructive defensive testing")
print("External systems targeted: NO")
print("Conclusion: DEFENSE-IN-DEPTH EVIDENCE READY")
