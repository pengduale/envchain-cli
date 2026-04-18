"""Compare two snapshots or a snapshot against the live store."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

from envchain.store import list_keys, get_variable
from envchain.snapshot import restore_snapshot


class DiffEntry(NamedTuple):
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str]
    new_value: Optional[str]


def _load_snapshot_vars(snapshot_path: Path, passphrase: str) -> Dict[str, str]:
    """Restore snapshot into a temp dict by reading its store file directly."""
    raw = json.loads(snapshot_path.read_text())
    result: Dict[str, str] = {}
    from envchain.crypto import decrypt
    for key, token in raw.items():
        try:
            result[key] = decrypt(token, passphrase)
        except Exception:
            result[key] = "<unreadable>"
    return result


def diff_snapshots(
    snapshot_a: Path,
    snapshot_b: Path,
    passphrase: str,
) -> List[DiffEntry]:
    """Return diff between two snapshot files."""
    vars_a = _load_snapshot_vars(snapshot_a, passphrase)
    vars_b = _load_snapshot_vars(snapshot_b, passphrase)
    return _compute_diff(vars_a, vars_b)


def diff_snapshot_vs_live(
    snapshot_path: Path,
    store_path: Path,
    passphrase: str,
) -> List[DiffEntry]:
    """Return diff between a snapshot and the live store."""
    vars_snap = _load_snapshot_vars(snapshot_path, passphrase)
    vars_live: Dict[str, str] = {}
    for key in list_keys(store_path, passphrase):
        vars_live[key] = get_variable(store_path, key, passphrase)
    return _compute_diff(vars_snap, vars_live)


def _compute_diff(old: Dict[str, str], new: Dict[str, str]) -> List[DiffEntry]:
    entries: List[DiffEntry] = []
    all_keys = sorted(set(old) | set(new))
    for key in all_keys:
        if key in old and key not in new:
            entries.append(DiffEntry(key, "removed", old[key], None))
        elif key not in old and key in new:
            entries.append(DiffEntry(key, "added", None, new[key]))
        elif old[key] != new[key]:
            entries.append(DiffEntry(key, "changed", old[key], new[key]))
        else:
            entries.append(DiffEntry(key, "unchanged", old[key], new[key]))
    return entries
