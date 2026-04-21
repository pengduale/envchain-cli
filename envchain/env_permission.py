"""Per-key permission model: read, write, delete."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_PERMISSIONS = {"read", "write", "delete"}


def _permission_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_permissions.json"


def _load_permissions(store_path: str) -> dict:
    p = _permission_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_permissions(store_path: str, data: dict) -> None:
    _permission_path(store_path).write_text(json.dumps(data, indent=2))


class PermissionResult:
    def __init__(self, key: str, permissions: list[str], ok: bool, message: str = ""):
        self.key = key
        self.permissions = permissions
        self.ok = ok
        self.message = message

    def __repr__(self) -> str:
        return f"PermissionResult(key={self.key!r}, permissions={self.permissions}, ok={self.ok})"


def set_permissions(store_path: str, key: str, permissions: list[str]) -> PermissionResult:
    invalid = set(permissions) - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}. Must be subset of {VALID_PERMISSIONS}")
    if not permissions:
        raise ValueError("Permissions list must not be empty")
    data = _load_permissions(store_path)
    data[key] = sorted(set(permissions))
    _save_permissions(store_path, data)
    return PermissionResult(key=key, permissions=data[key], ok=True, message="permissions set")


def get_permissions(store_path: str, key: str) -> Optional[list[str]]:
    data = _load_permissions(store_path)
    return data.get(key)


def remove_permissions(store_path: str, key: str) -> bool:
    data = _load_permissions(store_path)
    if key not in data:
        return False
    del data[key]
    _save_permissions(store_path, data)
    return True


def has_permission(store_path: str, key: str, permission: str) -> bool:
    perms = get_permissions(store_path, key)
    if perms is None:
        return True  # no restrictions means all allowed
    return permission in perms


def list_permissions(store_path: str) -> dict[str, list[str]]:
    return dict(_load_permissions(store_path))
