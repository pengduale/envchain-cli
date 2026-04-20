"""Track value change history for environment variables."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


def _history_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_history.json"


def _load_history(store_path: Path) -> dict:
    p = _history_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_history(store_path: Path, data: dict) -> None:
    _history_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class HistoryEntry:
    key: str
    timestamp: float
    action: str  # "set" | "delete"
    preview: Optional[str] = None  # first 4 chars of value, masked

    def __repr__(self) -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        return f"HistoryEntry(key={self.key!r}, action={self.action!r}, at={ts})"


def record_event(
    store_path: Path,
    key: str,
    action: str,
    value: Optional[str] = None,
    max_per_key: int = 50,
) -> HistoryEntry:
    """Append a history event for *key* and return the new entry."""
    if action not in ("set", "delete"):
        raise ValueError(f"Invalid action: {action!r}. Must be 'set' or 'delete'.")
    preview = None
    if value is not None:
        preview = (value[:4] + "****") if len(value) > 4 else "****"
    entry = HistoryEntry(key=key, timestamp=time.time(), action=action, preview=preview)
    data = _load_history(store_path)
    events = data.get(key, [])
    events.append(asdict(entry))
    if len(events) > max_per_key:
        events = events[-max_per_key:]
    data[key] = events
    _save_history(store_path, data)
    return entry


def get_history(store_path: Path, key: str) -> List[HistoryEntry]:
    """Return all recorded history entries for *key*, oldest first."""
    data = _load_history(store_path)
    return [HistoryEntry(**e) for e in data.get(key, [])]


def clear_history(store_path: Path, key: Optional[str] = None) -> int:
    """Clear history for *key* (or all keys). Returns number of entries removed."""
    data = _load_history(store_path)
    if key is not None:
        removed = len(data.pop(key, []))
    else:
        removed = sum(len(v) for v in data.values())
        data = {}
    _save_history(store_path, data)
    return removed


def list_keys_with_history(store_path: Path) -> List[str]:
    """Return keys that have at least one history entry."""
    return list(_load_history(store_path).keys())
