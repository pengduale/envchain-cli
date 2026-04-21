"""Manage visibility settings for stored environment variables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("public", "internal", "private", "secret")


def _visibility_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_visibility.json"


def _load_visibility(store_path: Path) -> dict:
    p = _visibility_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_visibility(store_path: Path, data: dict) -> None:
    _visibility_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class VisibilityResult:
    key: str
    level: str
    ok: bool
    message: str = ""

    def __repr__(self) -> str:
        return f"VisibilityResult(key={self.key!r}, level={self.level!r}, ok={self.ok})"


def set_visibility(store_path: Path, key: str, level: str) -> VisibilityResult:
    """Set the visibility level for a key."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid visibility level {level!r}. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load_visibility(store_path)
    data[key] = level
    _save_visibility(store_path, data)
    return VisibilityResult(key=key, level=level, ok=True, message=f"Set to {level!r}")


def get_visibility(store_path: Path, key: str) -> Optional[str]:
    """Return the visibility level for a key, or None if not set."""
    return _load_visibility(store_path).get(key)


def remove_visibility(store_path: Path, key: str) -> bool:
    """Remove the visibility setting for a key. Returns True if it existed."""
    data = _load_visibility(store_path)
    if key not in data:
        return False
    del data[key]
    _save_visibility(store_path, data)
    return True


def list_visibility(store_path: Path) -> dict[str, str]:
    """Return a mapping of key -> visibility level for all tracked keys."""
    return dict(_load_visibility(store_path))
