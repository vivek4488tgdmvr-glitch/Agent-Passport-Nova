from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .models import AgentPeer, DelegationRequest, DelegationResult
from .token import DelegationToken


class DelegationEngine:
    """Checks and enforces scoped, expiring, single/reusable delegation tokens."""

    def __init__(self, peers: list[AgentPeer] | None = None):
        self._peers = {peer.agent_id: peer for peer in (peers or [])}
        self._uses: dict[str, int] = {}
        self._audit: list[dict[str, Any]] = []

    def register(self, peer: AgentPeer) -> None:
        if not peer.agent_id:
            raise ValueError("agent_id is required")
        self._peers[peer.agent_id] = peer

    def get(self, agent_id: str) -> AgentPeer | None:
        return self._peers.get(agent_id)

    def evaluate(self, request: DelegationRequest) -> DelegationResult:
        if request.max_uses < 1:
            return DelegationResult("DENIED", request.requester_id, request.target_id,
                                    reason="max_uses must be at least 1")
        requester = self.get(request.requester_id)
        target = self.get(request.target_id)
        if requester is None:
            return DelegationResult("DENIED", request.requester_id, request.target_id,
                                    reason="requester is not registered")
        if target is None:
            return DelegationResult("DENIED", request.requester_id, request.target_id,
                                    reason="target is not registered")
        if requester.agent_id == target.agent_id:
            return DelegationResult("DENIED", request.requester_id, request.target_id,
                                    reason="self-delegation is not allowed")
        missing_capabilities = tuple(sorted(set(request.capabilities) - set(target.capabilities)))
        missing_tools = tuple(sorted(set(request.tools) - set(target.tools)))
        if missing_capabilities or missing_tools:
            return DelegationResult("DENIED", request.requester_id, request.target_id,
                                    missing_capabilities=missing_capabilities,
                                    missing_tools=missing_tools,
                                    reason="target cannot satisfy the requested scope")
        return DelegationResult("ALLOWED", request.requester_id, request.target_id,
                                reason="target satisfies the requested delegation scope")

    def require(self, request: DelegationRequest) -> DelegationResult:
        result = self.evaluate(request)
        if not result.allowed:
            raise PermissionError(result.pretty())
        return result

    def issue(self, request: DelegationRequest, ttl_seconds: int | None = 300) -> DelegationToken:
        self.require(request)
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive or None")
        expires_at = None
        if ttl_seconds is not None:
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()
        token = DelegationToken(
            request.requester_id, request.target_id,
            request.capabilities, request.tools, request.purpose,
            request.max_uses, expires_at,
        )
        self._audit_event("ISSUED", token, "delegation token issued")
        return token

    def consume(self, token: DelegationToken, request: DelegationRequest,
                now: datetime | None = None) -> DelegationResult:
        """Validate one use and atomically record it in the in-memory replay ledger."""
        if token.requester_id != request.requester_id or token.target_id != request.target_id:
            return self._deny(token, request, "token principal mismatch")
        if token.is_expired(now):
            return self._deny(token, request, "delegation token expired")
        used = self._uses.get(token.token_id, 0)
        if used >= token.max_uses:
            return self._deny(token, request, "delegation token replay/max-use limit reached")

        requested_caps = set(request.capabilities)
        requested_tools = set(request.tools)
        if not requested_caps.issubset(token.capabilities) or not requested_tools.issubset(token.tools):
            return self._deny(token, request, "permission escalation: requested scope exceeds token scope")
        if request.purpose and token.purpose and request.purpose != token.purpose:
            return self._deny(token, request, "purpose mismatch")

        self._uses[token.token_id] = used + 1
        result = DelegationResult("ALLOWED", request.requester_id, request.target_id,
                                  reason=f"token use accepted ({used + 1}/{token.max_uses})")
        self._audit_event("CONSUMED", token, result.reason)
        return result

    def usage_count(self, token: DelegationToken) -> int:
        return self._uses.get(token.token_id, 0)

    def audit_log(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(event) for event in self._audit)

    def _deny(self, token: DelegationToken, request: DelegationRequest, reason: str) -> DelegationResult:
        self._audit_event("DENIED", token, reason)
        return DelegationResult("DENIED", request.requester_id, request.target_id, reason=reason)

    def _audit_event(self, event: str, token: DelegationToken, reason: str) -> None:
        self._audit.append({
            "event": event,
            "token_id": token.token_id,
            "requester_id": token.requester_id,
            "target_id": token.target_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
