"""Badge system for annotating environment variables with status badges."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_BADGES = {"stable", "experimental", "deprecated", "internal", "public", "critical"}


def _badge_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_badges.json"


def _load_badges(store_path: Path) -> Dict[str, List[str]]:
    p = _badge_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_badges(store_path: Path, data: Dict[str, List[str]]) -> None:
    _badge_path(store_path).write_text(json.dumps(data, indent=2))


class BadgeResult:
    def __init__(self, key: str, badges: List[str], ok: bool, message: str = ""):
        self.key = key
        self.badges = badges
        self.ok = ok
        self.message = message

    def __repr__(self) -> str:
        return f"BadgeResult(key={self.key!r}, badges={self.badges}, ok={self.ok})"


def add_badge(store_path: Path, key: str, badge: str) -> BadgeResult:
    if badge not in VALID_BADGES:
        raise ValueError(f"Invalid badge {badge!r}. Valid: {sorted(VALID_BADGES)}")
    data = _load_badges(store_path)
    current = data.get(key, [])
    if badge not in current:
        current.append(badge)
        data[key] = current
        _save_badges(store_path, data)
    return BadgeResult(key=key, badges=list(current), ok=True, message=f"Badge '{badge}' added.")


def remove_badge(store_path: Path, key: str, badge: str) -> BadgeResult:
    data = _load_badges(store_path)
    current = data.get(key, [])
    if badge not in current:
        return BadgeResult(key=key, badges=list(current), ok=False, message=f"Badge '{badge}' not found.")
    current.remove(badge)
    data[key] = current
    _save_badges(store_path, data)
    return BadgeResult(key=key, badges=list(current), ok=True, message=f"Badge '{badge}' removed.")


def get_badges(store_path: Path, key: str) -> Optional[List[str]]:
    data = _load_badges(store_path)
    return data.get(key)


def list_all_badges(store_path: Path) -> Dict[str, List[str]]:
    return {k: v for k, v in _load_badges(store_path).items() if v}
