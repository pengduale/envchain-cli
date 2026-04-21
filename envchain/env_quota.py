"""Quota management: enforce per-store limits on number of variables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _quota_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_quota.json"


def _load_quota(store_path: Path) -> dict:
    p = _quota_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quota(store_path: Path, data: dict) -> None:
    _quota_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class QuotaResult:
    ok: bool
    key: str
    limit: Optional[int]
    current: int
    message: str

    def __repr__(self) -> str:
        return f"<QuotaResult key={self.key!r} ok={self.ok} {self.current}/{self.limit}>"


def set_quota(store_path: Path, profile: str, limit: int) -> QuotaResult:
    """Set the maximum number of variables allowed for a profile."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    data = _load_quota(store_path)
    data[profile] = limit
    _save_quota(store_path, data)
    return QuotaResult(ok=True, key=profile, limit=limit, current=0,
                       message=f"Quota for '{profile}' set to {limit}.")


def get_quota(store_path: Path, profile: str) -> Optional[int]:
    """Return the quota limit for a profile, or None if unset."""
    return _load_quota(store_path).get(profile)


def remove_quota(store_path: Path, profile: str) -> bool:
    """Remove the quota for a profile. Returns True if it existed."""
    data = _load_quota(store_path)
    if profile not in data:
        return False
    del data[profile]
    _save_quota(store_path, data)
    return True


def check_quota(store_path: Path, profile: str, current_count: int) -> QuotaResult:
    """Check whether adding one more variable would exceed the quota."""
    limit = get_quota(store_path, profile)
    if limit is None:
        return QuotaResult(ok=True, key=profile, limit=None, current=current_count,
                           message="No quota set.")
    if current_count >= limit:
        return QuotaResult(ok=False, key=profile, limit=limit, current=current_count,
                           message=f"Quota exceeded: {current_count}/{limit} variables.")
    return QuotaResult(ok=True, key=profile, limit=limit, current=current_count,
                       message=f"Within quota: {current_count}/{limit} variables.")


def list_quotas(store_path: Path) -> dict:
    """Return all profile quotas as a dict."""
    return dict(_load_quota(store_path))
