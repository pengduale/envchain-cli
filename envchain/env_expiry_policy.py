"""Expiry policy management for envchain variables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _policy_path(store_path: Path) -> Path:
    return store_path / ".expiry_policies.json"


def _load_policies(store_path: Path) -> dict:
    p = _policy_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(store_path: Path, data: dict) -> None:
    _policy_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ExpiryPolicyResult:
    key: str
    max_age_days: Optional[int]
    warn_before_days: Optional[int]
    action: str  # "warn" | "delete" | "lock"
    ok: bool
    message: str

    def __repr__(self) -> str:
        return (
            f"ExpiryPolicyResult(key={self.key!r}, max_age_days={self.max_age_days}, "
            f"action={self.action!r}, ok={self.ok})"
        )


VALID_ACTIONS = {"warn", "delete", "lock"}


def set_expiry_policy(
    store_path: Path,
    key: str,
    max_age_days: int,
    warn_before_days: int = 3,
    action: str = "warn",
) -> ExpiryPolicyResult:
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action {action!r}. Must be one of {VALID_ACTIONS}.")
    if max_age_days < 1:
        raise ValueError("max_age_days must be >= 1.")
    if warn_before_days < 0:
        raise ValueError("warn_before_days must be >= 0.")
    data = _load_policies(store_path)
    data[key] = {
        "max_age_days": max_age_days,
        "warn_before_days": warn_before_days,
        "action": action,
    }
    _save_policies(store_path, data)
    return ExpiryPolicyResult(
        key=key,
        max_age_days=max_age_days,
        warn_before_days=warn_before_days,
        action=action,
        ok=True,
        message=f"Expiry policy set for {key!r}.",
    )


def get_expiry_policy(store_path: Path, key: str) -> Optional[dict]:
    data = _load_policies(store_path)
    return data.get(key)


def remove_expiry_policy(store_path: Path, key: str) -> bool:
    data = _load_policies(store_path)
    if key not in data:
        return False
    del data[key]
    _save_policies(store_path, data)
    return True


def list_expiry_policies(store_path: Path) -> dict:
    return _load_policies(store_path)
