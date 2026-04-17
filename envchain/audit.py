"""Audit log for envchain operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILENAME = ".envchain_audit.jsonl"


def _audit_path(store_dir: str) -> Path:
    return Path(store_dir) / AUDIT_FILENAME


def log_event(store_dir: str, action: str, key: str, extra: dict = None) -> None:
    """Append an audit event to the log file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
    }
    if extra:
        entry.update(extra)
    path = _audit_path(store_dir)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_events(store_dir: str) -> list[dict]:
    """Return all audit events from the log file."""
    path = _audit_path(store_dir)
    if not path.exists():
        return []
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_log(store_dir: str) -> None:
    """Delete the audit log file."""
    path = _audit_path(store_dir)
    if path.exists():
        os.remove(path)
