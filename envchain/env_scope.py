"""Scope-based variable filtering: restrict which keys are visible per scope."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Optional


@dataclass
class ScopeResult:
    scope: str
    keys: list[str] = field(default_factory=list)
    action: str = "ok"

    def __repr__(self) -> str:
        return f"<ScopeResult scope={self.scope!r} keys={self.keys} action={self.action!r}>"


def _scope_path(store_dir: str) -> Path:
    return Path(store_dir) / ".scope_map.json"


def _load_scopes(store_dir: str) -> dict:
    p = _scope_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_scopes(store_dir: str, data: dict) -> None:
    _scope_path(store_dir).write_text(json.dumps(data, indent=2))


def set_scope(store_dir: str, scope: str, keys: list[str]) -> ScopeResult:
    data = _load_scopes(store_dir)
    data[scope] = list(keys)
    _save_scopes(store_dir, data)
    return ScopeResult(scope=scope, keys=list(keys), action="set")


def get_scope(store_dir: str, scope: str) -> Optional[list[str]]:
    return _load_scopes(store_dir).get(scope)


def remove_scope(store_dir: str, scope: str) -> bool:
    data = _load_scopes(store_dir)
    if scope not in data:
        return False
    del data[scope]
    _save_scopes(store_dir, data)
    return True


def list_scopes(store_dir: str) -> dict[str, list[str]]:
    return _load_scopes(store_dir)


def filter_keys_by_scope(store_dir: str, scope: str, all_keys: list[str]) -> list[str]:
    allowed = get_scope(store_dir, scope)
    if allowed is None:
        return all_keys
    return [k for k in all_keys if k in allowed]
