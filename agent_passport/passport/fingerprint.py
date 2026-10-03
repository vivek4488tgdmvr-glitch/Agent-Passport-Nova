from __future__ import annotations

import hashlib
import json

from .schema import Passport


def fingerprint(passport: Passport) -> str:
    """Return a deterministic SHA-256 fingerprint of passport contents."""
    payload = passport.model_dump(mode="json")
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
