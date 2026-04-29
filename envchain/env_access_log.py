"""Per-key access log: records read/write/delete events for individual keys."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _access_log_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_access_log.json"


def _load_log(store_path: Path) -> dict:
    p = _access_log_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_log(store_path: Path, data: dict) -> None:
    _access_log_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class AccessEntry:
    key: str
    action: str  # "read", "write", "delete"
    timestamp: str
    actor: Optional[str] = None

    def __repr__(self) -> str:
        actor_part = f" by {self.actor}" if self.actor else ""
        return f"<AccessEntry {self.action} {self.key!r}{actor_part} at {self.timestamp}>"


VALID_ACTIONS = {"read", "write", "delete"}


def record_access(store_path: Path, key: str, action: str, actor: Optional[str] = None) -> AccessEntry:
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action {action!r}. Must be one of {sorted(VALID_ACTIONS)}.")
    if not key:
        raise ValueError("Key must not be empty.")

    data = _load_log(store_path)
    entries = data.get(key, [])
    ts = datetime.now(timezone.utc).isoformat()
    entry = AccessEntry(key=key, action=action, timestamp=ts, actor=actor)
    entries.append(asdict(entry))
    data[key] = entries
    _save_log(store_path, data)
    return entry


def get_access_log(store_path: Path, key: str) -> List[AccessEntry]:
    data = _load_log(store_path)
    return [AccessEntry(**e) for e in data.get(key, [])]


def clear_access_log(store_path: Path, key: str) -> bool:
    data = _load_log(store_path)
    if key not in data:
        return False
    del data[key]
    _save_log(store_path, data)
    return True


def all_accessed_keys(store_path: Path) -> List[str]:
    return list(_load_log(store_path).keys())
