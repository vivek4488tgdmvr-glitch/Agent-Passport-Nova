from __future__ import annotations

from ..security import PermissionPolicy


def verify_policy(policy: PermissionPolicy) -> dict:
    overlap = set(policy.allow) & set(policy.deny)
    return {
        "status": "PASS" if not overlap else "FAIL",
        "overlap": sorted(overlap),
        "policy": policy.to_dict(),
    }
