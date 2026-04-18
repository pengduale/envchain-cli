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
    snap_dir = _snapshot_dir(store_path)
    results = []
    for f in sorted(snap_dir.glob("*.json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        results.append({"file": f.name, "ts": meta["ts"], "label": meta.get("label"), "keys": list(meta["data"].keys())})
    return results


def restore_snapshot(store_path: Path, snapshot_name: str, passphrase: str) -> int:
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
    snap_file = _snapshot_dir(store_path) / snapshot_name
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    snap_file.unlink()
