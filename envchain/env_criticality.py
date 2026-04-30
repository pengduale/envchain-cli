"""Criticality level management for environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("low", "medium", "high", "critical")


def _criticality_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_criticality.json"


def _load_criticality(store_path: str) -> dict:
    p = _criticality_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_criticality(store_path: str, data: dict) -> None:
    _criticality_path(store_path).write_text(json.dumps(data, indent=2))


class CriticalityResult:
    def __init__(self, key: str, level: str, reason: Optional[str], ok: bool, error: Optional[str] = None):
        self.key = key
        self.level = level
        self.reason = reason
        self.ok = ok
        self.error = error

    def __repr__(self) -> str:
        if not self.ok:
            return f"CriticalityResult(key={self.key!r}, error={self.error!r})"
        return f"CriticalityResult(key={self.key!r}, level={self.level!r}, reason={self.reason!r})"


def set_criticality(store_path: str, key: str, level: str, reason: Optional[str] = None) -> CriticalityResult:
    if level not in VALID_LEVELS:
        return CriticalityResult(key, level, reason, ok=False,
                                  error=f"Invalid level {level!r}. Choose from {VALID_LEVELS}.")
    data = _load_criticality(store_path)
    data[key] = {"level": level, "reason": reason}
    _save_criticality(store_path, data)
    return CriticalityResult(key, level, reason, ok=True)


def get_criticality(store_path: str, key: str) -> Optional[CriticalityResult]:
    data = _load_criticality(store_path)
    if key not in data:
        return None
    entry = data[key]
    return CriticalityResult(key, entry["level"], entry.get("reason"), ok=True)


def remove_criticality(store_path: str, key: str) -> bool:
    data = _load_criticality(store_path)
    if key not in data:
        return False
    del data[key]
    _save_criticality(store_path, data)
    return True


def list_criticality(store_path: str) -> list[CriticalityResult]:
    data = _load_criticality(store_path)
    return [
        CriticalityResult(k, v["level"], v.get("reason"), ok=True)
        for k, v in data.items()
    ]
