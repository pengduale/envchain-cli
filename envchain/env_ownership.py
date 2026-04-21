"""Ownership tracking for environment variables."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _ownership_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_ownership.json"


def _load_ownership(store_path: str) -> dict:
    p = _ownership_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ownership(store_path: str, data: dict) -> None:
    _ownership_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class OwnershipResult:
    key: str
    owner: str
    team: Optional[str]
    ok: bool
    message: str

    def __repr__(self) -> str:
        return f"<OwnershipResult key={self.key!r} owner={self.owner!r} ok={self.ok}>"


def set_ownership(store_path: str, key: str, owner: str, team: Optional[str] = None) -> OwnershipResult:
    if not key or not key.strip():
        return OwnershipResult(key=key, owner=owner, team=team, ok=False, message="Key must not be empty")
    if not owner or not owner.strip():
        return OwnershipResult(key=key, owner=owner, team=team, ok=False, message="Owner must not be empty")
    data = _load_ownership(store_path)
    data[key] = {"owner": owner, "team": team}
    _save_ownership(store_path, data)
    return OwnershipResult(key=key, owner=owner, team=team, ok=True, message="Ownership set")


def get_ownership(store_path: str, key: str) -> Optional[OwnershipResult]:
    data = _load_ownership(store_path)
    entry = data.get(key)
    if entry is None:
        return None
    return OwnershipResult(key=key, owner=entry["owner"], team=entry.get("team"), ok=True, message="Found")


def remove_ownership(store_path: str, key: str) -> bool:
    data = _load_ownership(store_path)
    if key not in data:
        return False
    del data[key]
    _save_ownership(store_path, data)
    return True


def list_owned_by(store_path: str, owner: str) -> list[str]:
    data = _load_ownership(store_path)
    return [k for k, v in data.items() if v.get("owner") == owner]


def list_owned_by_team(store_path: str, team: str) -> list[str]:
    data = _load_ownership(store_path)
    return [k for k, v in data.items() if v.get("team") == team]
