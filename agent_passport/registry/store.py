from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..passport.signing import verify_signature
from .models import RegistryEntry, RegistryStatus


class PassportRegistry:
    """File-backed Passport registry with signed publication and verified retrieval."""

    def __init__(self, path: str | Path = ".agent-passport/registry.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[RegistryEntry]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = []
        return [RegistryEntry.from_dict(x) for x in data]

    def _write(self, entries: list[RegistryEntry]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps([e.to_dict() for e in entries], indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    @staticmethod
    def _fingerprint(passport: dict[str, Any]) -> str:
        raw = json.dumps(passport, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def make_passport_id(passport: dict[str, Any]) -> str:
        raw = json.dumps(passport, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return "ap_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def register(
        self,
        passport: dict[str, Any],
        *,
        issuer: str | None = None,
        public_key: str | None = None,
        replace: bool = False,
        require_signature: bool = False,
    ) -> RegistryEntry:
        """Publish a Passport. Optionally require and verify its Ed25519 signature."""
        if require_signature:
            if not public_key:
                raise ValueError("public_key is required when require_signature=True")
            result = verify_signature(passport, public_key)
            if result["status"] != "PASS":
                raise ValueError(f"Passport signature verification failed: {result['reason']}")

        entries = self._read()
        fp = self._fingerprint(passport)
        agent = passport.get("agent", {})
        passport_id = self.make_passport_id(passport)
        existing = [
            e for e in entries
            if e.passport_id == passport_id or (
                e.agent_id == agent.get("id")
                and e.version == agent.get("version")
                and e.fingerprint == fp
            )
        ]
        if existing and not replace:
            return existing[0]

        entry = RegistryEntry(
            passport_id=passport_id,
            agent_id=agent.get("id", "unknown"),
            name=agent.get("name", agent.get("id", "Unknown")),
            version=agent.get("version", "unknown"),
            fingerprint=fp,
            issuer=issuer or passport.get("signature", {}).get("issuer"),
            public_key=public_key,
            registered_at=datetime.now(timezone.utc).isoformat(),
            passport=passport,
        )
        if existing:
            entries = [e for e in entries if e.passport_id != existing[0].passport_id]
        entries.append(entry)
        self._write(entries)
        return entry

    def publish(self, passport: dict[str, Any], *, public_key: str, replace: bool = False) -> RegistryEntry:
        """Publish only a cryptographically signed Passport."""
        return self.register(passport, public_key=public_key, replace=replace, require_signature=True)

    def list(self, *, include_revoked: bool = False) -> list[RegistryEntry]:
        entries = self._read()
        if not include_revoked:
            entries = [e for e in entries if e.status != RegistryStatus.REVOKED]
        return sorted(entries, key=lambda e: (e.agent_id, e.version))

    def get(self, passport_id: str) -> RegistryEntry | None:
        return next((e for e in self._read() if e.passport_id == passport_id), None)

    def find_agent(self, agent_id: str) -> list[RegistryEntry]:
        return sorted([e for e in self._read() if e.agent_id == agent_id], key=lambda e: e.version)

    def versions(self, agent_id: str, *, include_revoked: bool = False) -> list[str]:
        return [e.version for e in self.find_agent(agent_id) if include_revoked or e.status != RegistryStatus.REVOKED]

    def latest(self, agent_id: str, *, include_revoked: bool = False) -> RegistryEntry | None:
        entries = [e for e in self.find_agent(agent_id) if include_revoked or e.status != RegistryStatus.REVOKED]
        return entries[-1] if entries else None

    def revoke(self, passport_id: str) -> RegistryEntry:
        entries = self._read()
        for entry in entries:
            if entry.passport_id == passport_id:
                entry.status = RegistryStatus.REVOKED
                self._write(entries)
                return entry
        raise KeyError(f"Passport not found: {passport_id}")

    def verify_registered(self, passport_id: str, *, verify_signature_on_retrieval: bool = False) -> dict[str, Any]:
        entry = self.get(passport_id)
        if entry is None:
            return {"status": "FAIL", "reason": "Passport not found"}
        if entry.status == RegistryStatus.REVOKED:
            return {"status": "FAIL", "reason": "Passport is revoked"}

        current = self._fingerprint(entry.passport or {})
        if current != entry.fingerprint:
            return {"status": "FAIL", "reason": "Registered Passport content no longer matches fingerprint"}

        signature_result = None
        if verify_signature_on_retrieval:
            if not entry.public_key:
                return {"status": "FAIL", "reason": "No public key registered for signature verification"}
            signature_result = verify_signature(entry.passport or {}, entry.public_key)
            if signature_result["status"] != "PASS":
                return {"status": "FAIL", "reason": signature_result.get("reason", "Signature verification failed"), "signature": signature_result}

        result = {
            "status": "PASS",
            "passport_id": entry.passport_id,
            "agent_id": entry.agent_id,
            "version": entry.version,
            "fingerprint": entry.fingerprint,
            "status_record": entry.status.value,
            "issuer": entry.issuer,
        }
        if signature_result is not None:
            result["signature"] = signature_result
        return result

    def retrieve_verified(self, passport_id: str) -> dict[str, Any]:
        """Retrieve an active Passport only after fingerprint and signature checks."""
        entry = self.get(passport_id)
        if entry is None:
            return {"status": "FAIL", "reason": "Passport not found"}
        result = self.verify_registered(passport_id, verify_signature_on_retrieval=bool(entry.public_key))
        if result["status"] != "PASS":
            return result
        return {**result, "passport": entry.passport}
