"""Defensive security controls for hostile or untrusted agent traffic.

This module is intentionally defensive: it does not execute commands, scan
networks, or provide offensive tooling. It adds fail-closed request validation,
rate limiting, replay protection, secret redaction, and tamper-evident audit
records around Passport operations.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    reason: str
    principal: str
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "principal": self.principal,
            "request_id": self.request_id,
        }


class RequestGuard:
    """Validate security-sensitive request metadata before processing it."""

    _principal = re.compile(r"^[A-Za-z0-9_.:@-]{1,128}$")
    _request_id = re.compile(r"^[A-Za-z0-9_.:@/-]{1,128}$")

    def __init__(self, *, max_body_bytes: int = 1_048_576, max_text: int = 4096):
        if max_body_bytes <= 0 or max_text <= 0:
            raise ValueError("limits must be positive")
        self.max_body_bytes = max_body_bytes
        self.max_text = max_text

    def validate(self, principal: str, *, request_id: str | None = None,
                 body: bytes | str | None = None, purpose: str = "") -> SecurityDecision:
        if not isinstance(principal, str) or not self._principal.fullmatch(principal):
            return SecurityDecision(False, "invalid principal", principal if isinstance(principal, str) else "<invalid>", request_id)
        if request_id is not None and (not isinstance(request_id, str) or not self._request_id.fullmatch(request_id)):
            return SecurityDecision(False, "invalid request id", principal, request_id)
        if body is not None:
            size = len(body) if isinstance(body, bytes) else len(body.encode("utf-8"))
            if size > self.max_body_bytes:
                return SecurityDecision(False, "request body exceeds configured limit", principal, request_id)
        if len(purpose) > self.max_text:
            return SecurityDecision(False, "purpose exceeds configured limit", principal, request_id)
        return SecurityDecision(True, "request accepted", principal, request_id)


class SlidingWindowRateLimiter:
    """Thread-safe per-principal sliding-window limiter; fails closed on bad limits."""

    def __init__(self, *, max_requests: int = 30, window_seconds: float = 60.0,
                 clock: Callable[[], float] | None = None):
        if max_requests < 1 or window_seconds <= 0:
            raise ValueError("max_requests must be >= 1 and window_seconds > 0")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock or time.monotonic
        self._events: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, principal: str) -> bool:
        now = self._clock()
        with self._lock:
            events = self._events.setdefault(principal, deque())
            cutoff = now - self.window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.max_requests:
                return False
            events.append(now)
            return True

    def remaining(self, principal: str) -> int:
        now = self._clock()
        with self._lock:
            events = self._events.setdefault(principal, deque())
            cutoff = now - self.window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            return max(0, self.max_requests - len(events))


class ReplayGuard:
    """Bounded nonce/request-id replay defense."""

    def __init__(self, *, max_entries: int = 10_000):
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self.max_entries = max_entries
        self._seen: dict[str, None] = {}
        self._lock = Lock()

    def accept_once(self, nonce: str) -> bool:
        if not isinstance(nonce, str) or not nonce or len(nonce) > 256:
            return False
        with self._lock:
            if nonce in self._seen:
                return False
            if len(self._seen) >= self.max_entries:
                # Remove the oldest insertion deterministically.
                self._seen.pop(next(iter(self._seen)))
            self._seen[nonce] = None
            return True


_SECRET_KEYS = {
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "authorization", "private_key", "private_key_b64", "access_token",
    "refresh_token", "credential", "credentials",
}


def redact_secrets(value: Any) -> Any:
    """Return a JSON-like copy with common credential fields redacted."""
    if isinstance(value, Mapping):
        return {
            str(k): ("[REDACTED]" if str(k).lower() in _SECRET_KEYS else redact_secrets(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(v) for v in value]
    if isinstance(value, tuple):
        return [redact_secrets(v) for v in value]
    return value


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class TamperEvidentAuditLog:
    """In-memory hash-chain audit log. Persist externally for distributed deployments."""

    GENESIS = "0" * 64

    def __init__(self):
        self._entries: list[dict[str, Any]] = []
        self._lock = Lock()

    def append(self, event: str, *, principal: str, result: str,
               details: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if not event or not principal:
            raise ValueError("event and principal are required")
        safe_details = redact_secrets(dict(details or {}))
        with self._lock:
            previous = self._entries[-1]["entry_hash"] if self._entries else self.GENESIS
            payload = {
                "sequence": len(self._entries),
                "event": event,
                "principal": principal,
                "result": result,
                "details": safe_details,
                "previous_hash": previous,
            }
            entry_hash = hashlib.sha256(_canonical(payload)).hexdigest()
            entry = {**payload, "entry_hash": entry_hash}
            self._entries.append(entry)
            return dict(entry)

    def entries(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(x) for x in self._entries)

    def verify(self) -> bool:
        previous = self.GENESIS
        for expected_sequence, entry in enumerate(self._entries):
            if entry.get("sequence") != expected_sequence or entry.get("previous_hash") != previous:
                return False
            payload = {k: entry[k] for k in ("sequence", "event", "principal", "result", "details", "previous_hash")}
            if hashlib.sha256(_canonical(payload)).hexdigest() != entry.get("entry_hash"):
                return False
            previous = entry["entry_hash"]
        return True
