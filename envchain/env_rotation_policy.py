"""Rotation policy management for environment variables."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

VALID_INTERVALS = {"daily", "weekly", "monthly", "quarterly", "yearly"}


def _policy_path(store_path: Path) -> Path:
    return store_path / ".rotation_policies.json"


def _load_policies(store_path: Path) -> dict:
    p = _policy_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(store_path: Path, data: dict) -> None:
    _policy_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class RotationPolicyResult:
    key: str
    interval: str
    notify_before_days: int
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        if self.ok:
            return f"<RotationPolicy {self.key!r} every={self.interval} notify={self.notify_before_days}d>"
        return f"<RotationPolicy error={self.error!r}>"


def set_rotation_policy(
    store_path: Path,
    key: str,
    interval: str,
    notify_before_days: int = 7,
) -> RotationPolicyResult:
    if not key:
        return RotationPolicyResult(key=key, interval=interval, notify_before_days=notify_before_days, ok=False, error="Key must not be empty")
    if interval not in VALID_INTERVALS:
        return RotationPolicyResult(key=key, interval=interval, notify_before_days=notify_before_days, ok=False,
                                    error=f"Invalid interval {interval!r}. Choose from {sorted(VALID_INTERVALS)}")
    if notify_before_days < 0:
        return RotationPolicyResult(key=key, interval=interval, notify_before_days=notify_before_days, ok=False,
                                    error="notify_before_days must be >= 0")
    data = _load_policies(store_path)
    data[key] = {"interval": interval, "notify_before_days": notify_before_days}
    _save_policies(store_path, data)
    return RotationPolicyResult(key=key, interval=interval, notify_before_days=notify_before_days, ok=True)


def get_rotation_policy(store_path: Path, key: str) -> Optional[RotationPolicyResult]:
    data = _load_policies(store_path)
    entry = data.get(key)
    if entry is None:
        return None
    return RotationPolicyResult(key=key, interval=entry["interval"],
                                notify_before_days=entry["notify_before_days"], ok=True)


def remove_rotation_policy(store_path: Path, key: str) -> bool:
    data = _load_policies(store_path)
    if key not in data:
        return False
    del data[key]
    _save_policies(store_path, data)
    return True


def list_rotation_policies(store_path: Path) -> list[RotationPolicyResult]:
    data = _load_policies(store_path)
    return [
        RotationPolicyResult(key=k, interval=v["interval"],
                             notify_before_days=v["notify_before_days"], ok=True)
        for k, v in data.items()
    ]
