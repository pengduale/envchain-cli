"""Group multiple variables under a named group for bulk operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _group_path(store_dir: str) -> Path:
    return Path(store_dir) / ".envchain_groups.json"


def _load_groups(store_dir: str) -> dict:
    p = _group_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(store_dir: str, data: dict) -> None:
    _group_path(store_dir).write_text(json.dumps(data, indent=2))


@dataclass
class GroupResult:
    group: str
    keys: List[str] = field(default_factory=list)
    success: bool = True
    message: str = ""

    def __repr__(self) -> str:
        return f"<GroupResult group={self.group!r} keys={self.keys} success={self.success}>"


def create_group(store_dir: str, group: str, keys: List[str]) -> GroupResult:
    """Create or overwrite a named group with the given keys."""
    if not group:
        return GroupResult(group=group, success=False, message="Group name must not be empty.")
    if not keys:
        return GroupResult(group=group, success=False, message="Key list must not be empty.")
    data = _load_groups(store_dir)
    data[group] = list(keys)
    _save_groups(store_dir, data)
    return GroupResult(group=group, keys=list(keys))


def get_group(store_dir: str, group: str) -> Optional[List[str]]:
    """Return the list of keys for a group, or None if not found."""
    return _load_groups(store_dir).get(group)


def delete_group(store_dir: str, group: str) -> bool:
    """Remove a group. Returns True if it existed."""
    data = _load_groups(store_dir)
    if group not in data:
        return False
    del data[group]
    _save_groups(store_dir, data)
    return True


def list_groups(store_dir: str) -> List[str]:
    """Return all group names."""
    return list(_load_groups(store_dir).keys())


def add_key_to_group(store_dir: str, group: str, key: str) -> GroupResult:
    """Append a key to an existing group, creating it if necessary."""
    data = _load_groups(store_dir)
    keys = data.get(group, [])
    if key not in keys:
        keys.append(key)
    data[group] = keys
    _save_groups(store_dir, data)
    return GroupResult(group=group, keys=keys)


def remove_key_from_group(store_dir: str, group: str, key: str) -> GroupResult:
    """Remove a key from a group."""
    data = _load_groups(store_dir)
    keys = data.get(group, [])
    if key not in keys:
        return GroupResult(group=group, keys=keys, success=False, message=f"{key!r} not in group.")
    keys = [k for k in keys if k != key]
    data[group] = keys
    _save_groups(store_dir, data)
    return GroupResult(group=group, keys=keys)


def rename_group(store_dir: str, old_name: str, new_name: str) -> GroupResult:
    """Rename an existing group.

    Returns a failed GroupResult if the old group does not exist or if the
    new name is empty or already taken.
    """
    if not new_name:
        return GroupResult(group=old_name, success=False, message="New group name must not be empty.")
    data = _load_groups(store_dir)
    if old_name not in data:
        return GroupResult(group=old_name, success=False, message=f"Group {old_name!r} does not exist.")
    if new_name in data:
        return GroupResult(group=new_name, success=False, message=f"Group {new_name!r} already exists.")
    data[new_name] = data.pop(old_name)
    _save_groups(store_dir, data)
    return GroupResult(group=new_name, keys=data[new_name])
