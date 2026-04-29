"""Track the lineage (origin chain) of environment variables across profiles and operations."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional


def _lineage_path(store_path: Path) -> Path:
    return store_path / ".lineage.json"


def _load_lineage(store_path: Path) -> dict:
    p = _lineage_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_lineage(store_path: Path, data: dict) -> None:
    _lineage_path(store_path).write_text(json.dumps(data, indent=2))


class LineageEntry:
    def __init__(self, key: str, source_key: str, source_profile: str,
                 operation: str, timestamp: float, note: Optional[str] = None):
        self.key = key
        self.source_key = source_key
        self.source_profile = source_profile
        self.operation = operation
        self.timestamp = timestamp
        self.note = note

    def __repr__(self) -> str:
        return (f"LineageEntry(key={self.key!r}, source={self.source_key!r}, "
                f"profile={self.source_profile!r}, op={self.operation!r})")

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "source_key": self.source_key,
            "source_profile": self.source_profile,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "note": self.note,
        }

    @staticmethod
    def from_dict(d: dict) -> "LineageEntry":
        return LineageEntry(
            key=d["key"],
            source_key=d["source_key"],
            source_profile=d["source_profile"],
            operation=d["operation"],
            timestamp=d["timestamp"],
            note=d.get("note"),
        )


VALID_OPERATIONS = {"copy", "promote", "merge", "clone", "import", "manual"}


def record_lineage(store_path: Path, key: str, source_key: str,
                   source_profile: str, operation: str,
                   note: Optional[str] = None) -> LineageEntry:
    if operation not in VALID_OPERATIONS:
        raise ValueError(f"Invalid operation {operation!r}. Must be one of {VALID_OPERATIONS}.")
    data = _load_lineage(store_path)
    entry = LineageEntry(
        key=key,
        source_key=source_key,
        source_profile=source_profile,
        operation=operation,
        timestamp=time.time(),
        note=note,
    )
    data.setdefault(key, []).append(entry.to_dict())
    _save_lineage(store_path, data)
    return entry


def get_lineage(store_path: Path, key: str) -> List[LineageEntry]:
    data = _load_lineage(store_path)
    return [LineageEntry.from_dict(d) for d in data.get(key, [])]


def clear_lineage(store_path: Path, key: str) -> bool:
    data = _load_lineage(store_path)
    if key not in data:
        return False
    del data[key]
    _save_lineage(store_path, data)
    return True


def list_lineage_keys(store_path: Path) -> List[str]:
    return list(_load_lineage(store_path).keys())
