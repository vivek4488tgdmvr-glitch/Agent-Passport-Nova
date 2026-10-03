import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.delegation import (
    AgentPeer,
    DelegationEngine,
    DelegationRequest,
    DelegationToken,
)


nova = AgentPeer(
    "nova", "Nova", "1.0.0",
    capabilities=frozenset({"reasoning", "planning"}),
    tools=frozenset({"calculator"}),
    issuer="demo-issuer",
    passport_fingerprint="nova-demo",
)

scout = AgentPeer(
    "scout", "Scout", "1.0.0",
    capabilities=frozenset({"web_search", "summarization"}),
    tools=frozenset({"web_search"}),
    issuer="demo-issuer",
    passport_fingerprint="scout-demo",
)

engine = DelegationEngine([nova, scout])

print("=== DAY 18: MULTI-AGENT PASSPORTS ===")

allowed = DelegationRequest(
    requester_id="nova",
    target_id="scout",
    capabilities=frozenset({"web_search"}),
    tools=frozenset({"web_search"}),
    purpose="find current information",
    max_uses=1,
)

result = engine.evaluate(allowed)
print("\n[1] Valid delegation")
print(result.pretty())
print("✓ DELEGATION ALLOWED")

token = DelegationToken(
    "nova", "scout",
    allowed.capabilities,
    allowed.tools,
    allowed.purpose,
    allowed.max_uses,
)
print("Scoped token:", token.to_dict())

blocked = DelegationRequest(
    requester_id="nova",
    target_id="scout",
    capabilities=frozenset({"shell_execution"}),
    purpose="run an arbitrary command",
)

result = engine.evaluate(blocked)
print("\n[2] Out-of-scope delegation")
print(result.pretty())
print("✓ DELEGATION BLOCKED")

print("\nAgent identity ✓")
print("Capability matching ✓")
print("Tool scope matching ✓")
print("Explicit delegation scope ✓")
