"""Backup and restore the entire envchain store as an encrypted archive."""

import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path


def _backup_dir(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_backups"


def create_backup(store_path: str, label: str = "") -> str:
    """Create a compressed tar backup of the store directory. Returns backup path."""
    store = Path(store_path)
    if not store.exists():
        raise FileNotFoundError(f"Store path does not exist: {store_path}")

    backup_dir = _backup_dir(store_path)
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    name = f"backup_{ts}_{label}" if label else f"backup_{ts}"
    archive_path = backup_dir / f"{name}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(store, arcname=store.name)

    meta = {"created_at": ts, "label": label, "source": str(store)}
    meta_path = backup_dir / f"{name}.json"
    meta_path.write_text(json.dumps(meta, indent=2))

    return str(archive_path)


def list_backups(store_path: str) -> list[dict]:
    """List available backups with metadata."""
    backup_dir = _backup_dir(store_path)
    if not backup_dir.exists():
        return []

    results = []
    for meta_file in sorted(backup_dir.glob("backup_*.json")):
        data = json.loads(meta_file.read_text())
        archive = meta_file.with_suffix(".tar.gz")
        data["path"] = str(archive)
        data["exists"] = archive.exists()
        results.append(data)
    return results


def restore_backup(backup_path: str, target_dir: str, overwrite: bool = False) -> None:
    """Restore a backup archive into target_dir."""
    archive = Path(backup_path)
    if not archive.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    target = Path(target_dir)
    if target.exists() and not overwrite:
        raise FileExistsError(f"Target exists (use overwrite=True): {target_dir}")
    if target.exists():
        shutil.rmtree(target)

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(tmp)
        extracted = next(Path(tmp).iterdir())
        shutil.copytree(str(extracted), str(target))


def delete_backup(backup_path: str) -> bool:
    """Delete a backup archive and its metadata. Returns True if deleted."""
    archive = Path(backup_path)
    meta = archive.with_suffix("").with_suffix(".json")
    if not archive.exists():
        return False
    archive.unlink(missing_ok=True)
    meta.unlink(missing_ok=True)
    return True
