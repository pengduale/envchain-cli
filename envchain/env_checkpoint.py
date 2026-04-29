"""Checkpoint support: save and restore named variable checkpoints per profile."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envchain.store import get_variable, set_variable, list_keys


def _checkpoint_dir(store_path: Path) -> Path:
    d = store_path.parent / ".envchain_checkpoints"
    d.mkdir(exist_ok=True)
    return d


def _checkpoint_file(store_path: Path, name: str) -> Path:
    safe = name.replace("/", "_").replace("\\", "_")
    return _checkpoint_dir(store_path) / f"{safe}.json"


@dataclass
class CheckpointResult:
    name: str
    keys_saved: int
    created_at: float
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        return f"<CheckpointResult name={self.name!r} keys={self.keys_saved} ok={self.ok}>"


def create_checkpoint(
    store_path: Path, passphrase: str, name: str, profile: str = "default"
) -> CheckpointResult:
    """Snapshot all current variable values into a named checkpoint."""
    keys = list_keys(store_path)
    if not keys:
        return CheckpointResult(name=name, keys_saved=0, created_at=time.time(), ok=False, error="store is empty")

    data: dict[str, str] = {}
    for key in keys:
        val = get_variable(store_path, passphrase, key)
        if val is not None:
            data[key] = val

    payload = {"profile": profile, "created_at": time.time(), "vars": data}
    _checkpoint_file(store_path, name).write_text(json.dumps(payload, indent=2))
    return CheckpointResult(name=name, keys_saved=len(data), created_at=payload["created_at"], ok=True)


def restore_checkpoint(
    store_path: Path, passphrase: str, name: str, overwrite: bool = False
) -> CheckpointResult:
    """Restore variable values from a named checkpoint."""
    cp = _checkpoint_file(store_path, name)
    if not cp.exists():
        return CheckpointResult(name=name, keys_saved=0, created_at=0.0, ok=False, error=f"checkpoint '{name}' not found")

    payload = json.loads(cp.read_text())
    restored = 0
    for key, val in payload["vars"].items():
        existing = get_variable(store_path, passphrase, key)
        if existing is not None and not overwrite:
            continue
        set_variable(store_path, passphrase, key, val)
        restored += 1
    return CheckpointResult(name=name, keys_saved=restored, created_at=payload["created_at"], ok=True)


def list_checkpoints(store_path: Path) -> list[dict]:
    """Return metadata for all saved checkpoints."""
    results = []
    for f in sorted(_checkpoint_dir(store_path).glob("*.json")):
        try:
            payload = json.loads(f.read_text())
            results.append({"name": f.stem, "profile": payload.get("profile", "default"), "created_at": payload.get("created_at"), "keys": len(payload.get("vars", {}))})
        except Exception:
            pass
    return results


def delete_checkpoint(store_path: Path, name: str) -> bool:
    """Delete a named checkpoint file.

    Returns True if the checkpoint was found and deleted, False if it did not exist.
    Raises OSError if the file exists but cannot be removed.
    """
    cp = _checkpoint_file(store_path, name)
    if not cp.exists():
        return False
    cp.unlink()
    return True
