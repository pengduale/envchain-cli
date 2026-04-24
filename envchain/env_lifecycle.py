"""Lifecycle state management for environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

VALID_STATES = ["active", "deprecated", "retired", "draft"]


def _lifecycle_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_lifecycle.json"


def _load_lifecycle(store_path: Path) -> dict:
    p = _lifecycle_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_lifecycle(store_path: Path, data: dict) -> None:
    _lifecycle_path(store_path).write_text(json.dumps(data, indent=2))


class LifecycleResult:
    def __init__(self, key: str, state: str, ok: bool, message: str = ""):
        self.key = key
        self.state = state
        self.ok = ok
        self.message = message

    def __repr__(self) -> str:
        return f"LifecycleResult(key={self.key!r}, state={self.state!r}, ok={self.ok})"


def set_lifecycle(store_path: Path, key: str, state: str) -> LifecycleResult:
    """Set the lifecycle state for a key."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state {state!r}. Must be one of {VALID_STATES}.")
    data = _load_lifecycle(store_path)
    data[key] = state
    _save_lifecycle(store_path, data)
    return LifecycleResult(key=key, state=state, ok=True, message=f"State set to {state!r}.")


def get_lifecycle(store_path: Path, key: str) -> Optional[str]:
    """Return the lifecycle state for a key, or None if unset."""
    return _load_lifecycle(store_path).get(key)


def remove_lifecycle(store_path: Path, key: str) -> bool:
    """Remove lifecycle state for a key. Returns True if removed."""
    data = _load_lifecycle(store_path)
    if key not in data:
        return False
    del data[key]
    _save_lifecycle(store_path, data)
    return True


def list_by_state(store_path: Path, state: str) -> List[str]:
    """Return all keys with the given lifecycle state."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state {state!r}. Must be one of {VALID_STATES}.")
    data = _load_lifecycle(store_path)
    return [k for k, v in data.items() if v == state]


def list_all_lifecycle(store_path: Path) -> dict:
    """Return all key->state mappings."""
    return dict(_load_lifecycle(store_path))
