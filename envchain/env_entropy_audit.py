"""Audit stored variables for entropy (randomness) quality and flag weak secrets."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envchain.store import list_keys, get_variable


WEAK_THRESHOLD = 2.5
FAIR_THRESHOLD = 3.5


@dataclass
class EntropyAuditEntry:
    key: str
    entropy: float
    level: str  # "weak", "fair", "strong"
    note: Optional[str] = None

    def __repr__(self) -> str:
        return f"<EntropyAuditEntry key={self.key!r} entropy={self.entropy:.2f} level={self.level!r}>"


def _shannon_entropy(value: str) -> float:
    """Compute Shannon entropy (bits per character) for a string."""
    if not value:
        return 0.0
    freq: dict[str, int] = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _classify(entropy: float) -> str:
    if entropy < WEAK_THRESHOLD:
        return "weak"
    if entropy < FAIR_THRESHOLD:
        return "fair"
    return "strong"


def audit_store(store_path: Path, passphrase: str) -> List[EntropyAuditEntry]:
    """Audit all keys in the store and return entropy entries."""
    keys = list_keys(store_path)
    entries: List[EntropyAuditEntry] = []
    for key in sorted(keys):
        value = get_variable(store_path, key, passphrase)
        if value is None:
            continue
        entropy = _shannon_entropy(value)
        level = _classify(entropy)
        note = None
        if level == "weak":
            note = "Value appears too simple or repetitive — consider rotating."
        elif level == "fair":
            note = "Value has moderate entropy — may be acceptable."
        entries.append(EntropyAuditEntry(key=key, entropy=entropy, level=level, note=note))
    return entries


def summary(entries: List[EntropyAuditEntry]) -> dict:
    """Return a summary dict with counts per level."""
    counts: dict[str, int] = {"weak": 0, "fair": 0, "strong": 0}
    for e in entries:
        counts[e.level] += 1
    counts["total"] = len(entries)
    return counts
