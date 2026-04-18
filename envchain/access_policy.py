"""Access policy: restrict which keys a given 'role' can read or write."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional

_POLICY_FILE = ".envchain_policy.json"


def _policy_path(store_dir: str) -> Path:
    return Path(store_dir) / _POLICY_FILE


def _load_policies(store_dir: str) -> Dict[str, dict]:
    p = _policy_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(store_dir: str, data: Dict[str, dict]) -> None:
    _policy_path(store_dir).write_text(json.dumps(data, indent=2))


def set_policy(store_dir: str, role: str, allow_read: List[str], allow_write: List[str]) -> None:
    """Create or overwrite the policy for *role*."""
    policies = _load_policies(store_dir)
    policies[role] = {"allow_read": allow_read, "allow_write": allow_write}
    _save_policies(store_dir, policies)


def remove_policy(store_dir: str, role: str) -> bool:
    policies = _load_policies(store_dir)
    if role not in policies:
        return False
    del policies[role]
    _save_policies(store_dir, policies)
    return True


def get_policy(store_dir: str, role: str) -> Optional[dict]:
    return _load_policies(store_dir).get(role)


def list_policies(store_dir: str) -> List[str]:
    return list(_load_policies(store_dir).keys())


def can_read(store_dir: str, role: str, key: str) -> bool:
    policy = get_policy(store_dir, role)
    if policy is None:
        return False
    return "*" in policy["allow_read"] or key in policy["allow_read"]


def can_write(store_dir: str, role: str, key: str) -> bool:
    policy = get_policy(store_dir, role)
    if policy is None:
        return False
    return "*" in policy["allow_write"] or key in policy["allow_write"]
