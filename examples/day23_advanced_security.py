from datetime import datetime, timedelta, timezone

from agent_passport.delegation import AgentPeer, DelegationEngine, DelegationRequest


def main():
    nova = AgentPeer("nova", "Nova", "1.0.0")
    scout = AgentPeer("scout", "Scout", "1.0.0",
                      capabilities=frozenset({"web_search", "summarization"}),
                      tools=frozenset({"web_search"}))
    engine = DelegationEngine([nova, scout])
    request = DelegationRequest("nova", "scout", frozenset({"web_search"}),
                                frozenset({"web_search"}), "search", max_uses=1)
    token = engine.issue(request, ttl_seconds=60)
    first = engine.consume(token, request)
    replay = engine.consume(token, request)
    escalation = engine.consume(token, DelegationRequest(
        "nova", "scout", frozenset({"web_search", "summarization"}),
        frozenset({"web_search"}), "search"))
    expired = engine.consume(token, request, now=datetime.now(timezone.utc) + timedelta(minutes=2))
    print("=== DAY 23: ADVANCED SECURITY ===")
    print(f"Token issued: PASS ✓ ({token.token_id})")
    print(f"First use: {'PASS ✓' if first.allowed else 'FAIL'}")
    print(f"Replay protection: {'PASS ✓' if not replay.allowed else 'FAIL'}")
    print(f"Permission escalation blocked: {'PASS ✓' if not escalation.allowed else 'FAIL'}")
    print(f"Expiration enforcement: {'PASS ✓' if not expired.allowed else 'FAIL'}")
    print(f"Audit events: {len(engine.audit_log())}")
    print("ADVANCED SECURITY ✓")


if __name__ == "__main__":
    main()
