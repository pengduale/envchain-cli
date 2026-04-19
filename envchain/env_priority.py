"""Priority ordering for environment variable resolution across profiles."""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Optional

from envchain.store import get_variable
from envchain.profile import get_profile_variable


def _priority_path(store_path: Path) -> Path:
    return store_path.parent / "priority.json"


def _load_priorities(store_path: Path) -> dict:
    p = _priority_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(store_path: Path, data: dict) -> None:
    _priority_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class PriorityResult:
    key: str
    value: Optional[str]
    resolved_from: Optional[str]  # profile name or "default"
    tried: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"<PriorityResult key={self.key!r} from={self.resolved_from!r}>"


def set_priority(store_path: Path, key: str, profiles: list[str]) -> None:
    """Set the resolution order (list of profile names) for a key."""
    if not profiles:
        raise ValueError("profiles list must not be empty")
    data = _load_priorities(store_path)
    data[key] = profiles
    _save_priorities(store_path, data)


def get_priority(store_path: Path, key: str) -> Optional[list[str]]:
    data = _load_priorities(store_path)
    return data.get(key)


def remove_priority(store_path: Path, key: str) -> bool:
    data = _load_priorities(store_path)
    if key not in data:
        return False
    del data[key]
    _save_priorities(store_path, data)
    return True


def resolve_variable(store_path: Path, key: str, passphrase: str) -> PriorityResult:
    """Resolve a variable using the configured priority order."""
    profiles = get_priority(store_path, key) or ["default"]
    tried = []
    for profile in profiles:
        tried.append(profile)
        try:
            if profile == "default":
                val = get_variable(store_path, key, passphrase)
            else:
                val = get_profile_variable(store_path, profile, key, passphrase)
            if val is not None:
                return PriorityResult(key=key, value=val, resolved_from=profile, tried=tried)
        except Exception:
            continue
    return PriorityResult(key=key, value=None, resolved_from=None, tried=tried)
