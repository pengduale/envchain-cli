"""Snapshot: save and restore full store state."""
from __future__ import annotations
import json
import time
from pathlib import Path
from envchain.store import list_keys, get_variable, set_variable


def _snapshot_dir(store_path: Path) -> Path:
    d = store_path.parent / ".snapshots"
    d.mkdir(exist_ok=True)
    return d


def create_snapshot(store_path: Path, passphrase: str, label: str | None = None) -> Path:
    """Create a snapshot of all variables in the store.

    Args:
        store_path: Path to the store file.
        passphrase: Passphrase used to decrypt store variables.
        label: Optional human-readable label appended to the snapshot filename.

    Returns:
        Path to the created snapshot file.

    Raises:
        ValueError: If the store is empty.
    """
    keys = list_keys(store_path)
    if not keys:
        raise ValueError("Store is empty; nothing to snapshot.")
    data = {}
    for key in keys:
        data[key] = get_variable(store_path, key, passphrase)
    ts = int(time.time())
    name = f"{ts}_{label}.json" if label else f"{ts}.json"
    snap_file = _snapshot_dir(store_path) / name
    snap_file.write_text(json.dumps({"ts": ts, "label": label, "data": data}), encoding="utf-8")
    return snap_file


def list_snapshots(store_path: Path) -> list[dict]:
    """List all available snapshots for the given store.

    Returns:
        A list of dicts with keys: file, ts, label, keys.
    """
    snap_dir = _snapshot_dir(store_path)
    results = []
    for f in sorted(snap_dir.glob("*.json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        results.append({"file": f.name, "ts": meta["ts"], "label": meta.get("label"), "keys": list(meta["data"].keys())})
    return results


def restore_snapshot(store_path: Path, snapshot_name: str, passphrase: str) -> int:
    """Restore variables from a snapshot into the store.

    Args:
        store_path: Path to the store file.
        snapshot_name: Filename of the snapshot (as returned by list_snapshots).
        passphrase: Passphrase used to encrypt restored variables.

    Returns:
        Number of variables restored.

    Raises:
        FileNotFoundError: If the snapshot file does not exist.
    """
    snap_file = _snapshot_dir(store_path) / snapshot_name
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    meta = json.loads(snap_file.read_text(encoding="utf-8"))
    count = 0
    for key, value in meta["data"].items():
        set_variable(store_path, key, value, passphrase)
        count += 1
    return count


def delete_snapshot(store_path: Path, snapshot_name: str) -> None:
    """Delete a snapshot file.

    Args:
        store_path: Path to the store file.
        snapshot_name: Filename of the snapshot to delete.

    Raises:
        FileNotFoundError: If the snapshot file does not exist.
    """
    snap_file = _snapshot_dir(store_path) / snapshot_name
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    snap_file.unlink()


def get_snapshot(store_path: Path, snapshot_name: str) -> dict:
    """Load and return the metadata and data for a single snapshot.

    Args:
        store_path: Path to the store file.
        snapshot_name: Filename of the snapshot.

    Returns:
        A dict with keys: file, ts, label, keys.

    Raises:
        FileNotFoundError: If the snapshot file does not exist.
    """
    snap_file = _snapshot_dir(store_path) / snapshot_name
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    meta = json.loads(snap_file.read_text(encoding="utf-8"))
    return {"file": snap_file.name, "ts": meta["ts"], "label": meta.get("label"), "keys": list(meta["data"].keys())}
