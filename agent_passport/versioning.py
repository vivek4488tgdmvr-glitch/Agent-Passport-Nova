from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json


@dataclass
class PassportChange:
    path: str
    change: str
    before: Any = None
    after: Any = None

    def to_dict(self):
        return {"path": self.path, "change": self.change,
                "before": self.before, "after": self.after}


@dataclass
class PassportDiff:
    source_version: str
    target_version: str
    changes: list[PassportChange] = field(default_factory=list)

    @property
    def changed(self):
        return bool(self.changes)

    @property
    def summary(self):
        out = {"added": 0, "removed": 0, "modified": 0}
        for c in self.changes:
            out[c.change] += 1
        return out

    def to_dict(self):
        return {"source_version": self.source_version,
                "target_version": self.target_version,
                "changed": self.changed,
                "summary": self.summary,
                "changes": [c.to_dict() for c in self.changes]}

    def pretty(self):
        lines = [f"PASSPORT DIFF: {self.source_version} → {self.target_version}",
                 "-" * 56]
        if not self.changes:
            return "\n".join(lines + ["No changes."])
        for c in self.changes:
            symbol = { "added": "+", "removed": "-", "modified": "~" }[c.change]
            lines.append(f"{symbol} {c.path}")
            if c.change == "modified":
                lines.append(f"    before: {json.dumps(c.before, sort_keys=True)}")
                lines.append(f"    after:  {json.dumps(c.after, sort_keys=True)}")
            else:
                value = c.after if c.change == "added" else c.before
                lines.append(f"    value: {json.dumps(value, sort_keys=True)}")
        return "\n".join(lines)


def _version(p):
    return str(p.get("agent", {}).get("version", "unknown"))


def _walk(before, after, path, out):
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before) | set(after)):
            # Agent version is represented in the diff header, not as a
            # separate contract change.
            if path == "agent" and key == "version":
                continue
            child = f"{path}.{key}" if path else key
            if key not in before:
                out.append(PassportChange(child, "added", after=after[key]))
            elif key not in after:
                out.append(PassportChange(child, "removed", before=before[key]))
            else:
                _walk(before[key], after[key], child, out)
        return

    if isinstance(before, list) and isinstance(after, list):
        if before == after:
            return
        if all(isinstance(x, (str, int, float, bool)) or x is None
               for x in before + after):
            b, a = set(before), set(after)
            for value in sorted(a-b, key=str):
                out.append(PassportChange(f"{path}[]", "added", after=value))
            for value in sorted(b-a, key=str):
                out.append(PassportChange(f"{path}[]", "removed", before=value))
            return
        if all(isinstance(x, dict) for x in before + after):
            b = {json.dumps(x, sort_keys=True, separators=(",", ":")): x for x in before}
            a = {json.dumps(x, sort_keys=True, separators=(",", ":")): x for x in after}
            for key in sorted(a.keys() - b.keys()):
                out.append(PassportChange(f"{path}[]", "added", after=a[key]))
            for key in sorted(b.keys() - a.keys()):
                out.append(PassportChange(f"{path}[]", "removed", before=b[key]))
            return
        out.append(PassportChange(path, "modified", before=before, after=after))
        return

    if before != after:
        out.append(PassportChange(path, "modified", before=before, after=after))


def diff_passports(before: dict[str, Any], after: dict[str, Any]) -> PassportDiff:
    changes = []
    _walk(before, after, "", changes)
    return PassportDiff(_version(before), _version(after), changes)
