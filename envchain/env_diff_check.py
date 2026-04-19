"""Compare live environment variables against stored envchain values."""
from dataclasses import dataclass, field
from typing import Optional
import os

from envchain.store import get_variable, list_keys


@dataclass
class EnvDiffEntry:
    key: str
    stored: Optional[str]
    live: Optional[str]

    @property
    def status(self) -> str:
        if self.stored is None:
            return "live_only"
        if self.live is None:
            return "stored_only"
        if self.stored == self.live:
            return "match"
        return "mismatch"

    def __repr__(self) -> str:
        return f"EnvDiffEntry(key={self.key!r}, status={self.status!r})"


def diff_live_vs_stored(
    store_path: str,
    passphrase: str,
    keys: Optional[list] = None,
    include_live_only: bool = False,
) -> list:
    """Compare stored variables against the current process environment."""
    stored_keys = list_keys(store_path)
    results = []

    for key in (keys or stored_keys):
        try:
            stored_val = get_variable(store_path, key, passphrase)
        except Exception:
            stored_val = None
        live_val = os.environ.get(key)
        results.append(EnvDiffEntry(key=key, stored=stored_val, live=live_val))

    if include_live_only:
        for key, val in os.environ.items():
            if key not in stored_keys:
                results.append(EnvDiffEntry(key=key, stored=None, live=val))

    return results


def summary(entries: list) -> dict:
    counts = {"match": 0, "mismatch": 0, "stored_only": 0, "live_only": 0}
    for e in entries:
        counts[e.status] = counts.get(e.status, 0) + 1
    return counts
