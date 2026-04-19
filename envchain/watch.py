"""Watch a store file for changes and trigger a callback."""
from __future__ import annotations
import time
import os
from pathlib import Path
from typing import Callable, Optional


def _mtime(path: Path) -> Optional[float]:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def watch_store(
    store_path: Path,
    callback: Callable[[Path], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll store_path every *interval* seconds; call callback on change."""
    last = _mtime(store_path)
    iterations = 0
    while True:
        time.sleep(interval)
        current = _mtime(store_path)
        if current != last:
            last = current
            callback(store_path)
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break


def diff_on_change(store_path: Path, passphrase: str) -> Callable[[Path], None]:
    """Return a callback that prints changed keys when the store file changes."""
    from envchain.store import list_keys, get_variable

    snapshot: dict[str, str] = {}
    for key in list_keys(store_path):
        try:
            snapshot[key] = get_variable(store_path, key, passphrase)
        except Exception:
            pass

    def _cb(path: Path) -> None:
        nonlocal snapshot
        new: dict[str, str] = {}
        for key in list_keys(path):
            try:
                new[key] = get_variable(path, key, passphrase)
            except Exception:
                pass
        added = set(new) - set(snapshot)
        removed = set(snapshot) - set(new)
        changed = {k for k in new if k in snapshot and new[k] != snapshot[k]}
        for k in sorted(added):
            print(f"[watch] + {k} added")
        for k in sorted(removed):
            print(f"[watch] - {k} removed")
        for k in sorted(changed):
            print(f"[watch] ~ {k} changed")
        snapshot = new

    return _cb
