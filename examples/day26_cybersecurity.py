import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.security import (
    RequestGuard, SlidingWindowRateLimiter, ReplayGuard,
    TamperEvidentAuditLog,
)


def main():
    print("=== DAY 26: CYBERSECURITY HARDENING ===")
    guard = RequestGuard(max_body_bytes=1024)
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
    replay = ReplayGuard()
    audit = TamperEvidentAuditLog()

    checks = []
    checks.append(("INPUT VALIDATION", guard.validate("nova", request_id="req-26", body=b"safe").allowed))
    checks.append(("MALFORMED INPUT BLOCK", not guard.validate("../../attacker").allowed))
    checks.append(("RATE LIMIT", limiter.allow("nova") and limiter.allow("nova") and not limiter.allow("nova")))
    checks.append(("REPLAY PROTECTION", replay.accept_once("nonce-26") and not replay.accept_once("nonce-26")))
    audit.append("AUTHZ", principal="nova", result="ALLOW", details={"tool": "calculator", "api_key": "hidden"})
    checks.append(("TAMPER-EVIDENT AUDIT", audit.verify() and audit.entries()[0]["details"]["api_key"] == "[REDACTED]"))

    for name, ok in checks:
        print(f"{'✓' if ok else '✗'} {name}")
    print(f"\nSECURITY HARDENING: {'PASS' if all(x[1] for x in checks) else 'FAIL'}")


if __name__ == "__main__":
    main()
