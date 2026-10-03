from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .schema import Passport


SUPPORTED = {".yaml", ".yml", ".json"}


def read_raw(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Unsupported passport format: {path.suffix}")

    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)

    if not isinstance(data, dict):
        raise ValueError("Passport root must be an object.")
    return data


def load(path: str | Path) -> Passport:
    return Passport.model_validate(read_raw(path))


def export_passport(passport: Passport, path: str | Path) -> Path:
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError("Export must use .yaml, .yml, or .json")

    data = passport.model_dump(mode="json")
    if path.suffix.lower() == ".json":
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        path.write_text(
            yaml.safe_dump(data, sort_keys=False),
            encoding="utf-8",
        )
    return path
