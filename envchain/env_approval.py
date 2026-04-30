"""Approval workflow tracking for environment variables."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

VALID_STATUSES = {"pending", "approved", "rejected"}


def _approval_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_approval.json"


def _load_approvals(store_path: str) -> dict:
    p = _approval_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_approvals(store_path: str, data: dict) -> None:
    _approval_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ApprovalResult:
    ok: bool
    key: str
    status: Optional[str]
    approver: Optional[str]
    timestamp: Optional[str]
    message: Optional[str]

    def __repr__(self) -> str:
        return (
            f"ApprovalResult(ok={self.ok}, key={self.key!r}, "
            f"status={self.status!r}, approver={self.approver!r})"
        )


def set_approval(
    store_path: str,
    key: str,
    status: str,
    approver: Optional[str] = None,
    message: Optional[str] = None,
) -> ApprovalResult:
    if status not in VALID_STATUSES:
        return ApprovalResult(
            ok=False, key=key, status=None, approver=None,
            timestamp=None, message=f"Invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}"
        )
    if not key:
        return ApprovalResult(
            ok=False, key=key, status=None, approver=None,
            timestamp=None, message="Key must not be empty"
        )
    data = _load_approvals(store_path)
    ts = datetime.now(timezone.utc).isoformat()
    data[key] = {"status": status, "approver": approver, "timestamp": ts, "message": message}
    _save_approvals(store_path, data)
    return ApprovalResult(ok=True, key=key, status=status, approver=approver, timestamp=ts, message=message)


def get_approval(store_path: str, key: str) -> Optional[ApprovalResult]:
    data = _load_approvals(store_path)
    entry = data.get(key)
    if entry is None:
        return None
    return ApprovalResult(
        ok=True, key=key, status=entry["status"],
        approver=entry.get("approver"), timestamp=entry.get("timestamp"),
        message=entry.get("message")
    )


def remove_approval(store_path: str, key: str) -> bool:
    data = _load_approvals(store_path)
    if key not in data:
        return False
    del data[key]
    _save_approvals(store_path, data)
    return True


def list_approvals(store_path: str, status_filter: Optional[str] = None) -> list[ApprovalResult]:
    data = _load_approvals(store_path)
    results = []
    for k, v in data.items():
        if status_filter and v["status"] != status_filter:
            continue
        results.append(ApprovalResult(
            ok=True, key=k, status=v["status"],
            approver=v.get("approver"), timestamp=v.get("timestamp"),
            message=v.get("message")
        ))
    return results
