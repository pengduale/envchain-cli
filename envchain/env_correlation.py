"""env_correlation.py — Track correlations (relationships) between environment variables.

A correlation records that one key is logically related to another,
with an optional relationship type (e.g. 'same-service', 'derived-from',
'replaces', 'paired-with') and a free-text note.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Valid relationship types
# ---------------------------------------------------------------------------

VALID_RELATIONS = {
    "same-service",
    "derived-from",
    "replaces",
    "paired-with",
    "depends-on",
    "mirrors",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _correlation_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_correlations.json"


def _load_correlations(store_path: Path) -> dict:
    path = _correlation_path(store_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_correlations(store_path: Path, data: dict) -> None:
    path = _correlation_path(store_path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------

@dataclass
class CorrelationResult:
    ok: bool
    key: str
    related_key: str
    relation: str
    note: Optional[str] = None
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        if not self.ok:
            return f"CorrelationResult(error={self.error!r})"
        return (
            f"CorrelationResult(key={self.key!r}, related_key={self.related_key!r}, "
            f"relation={self.relation!r}, note={self.note!r})"
        )


@dataclass
class CorrelationEntry:
    related_key: str
    relation: str
    note: Optional[str] = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def add_correlation(
    store_path: Path,
    key: str,
    related_key: str,
    relation: str = "paired-with",
    note: Optional[str] = None,
) -> CorrelationResult:
    """Record that *key* is correlated with *related_key*."""
    if relation not in VALID_RELATIONS:
        return CorrelationResult(
            ok=False,
            key=key,
            related_key=related_key,
            relation=relation,
            error=f"Invalid relation {relation!r}. Choose from: {sorted(VALID_RELATIONS)}",
        )

    data = _load_correlations(store_path)
    entries = data.setdefault(key, [])

    # Avoid exact duplicates (same related_key + relation)
    for entry in entries:
        if entry["related_key"] == related_key and entry["relation"] == relation:
            return CorrelationResult(
                ok=True, key=key, related_key=related_key, relation=relation, note=note
            )

    entries.append({"related_key": related_key, "relation": relation, "note": note})
    _save_correlations(store_path, data)
    return CorrelationResult(ok=True, key=key, related_key=related_key, relation=relation, note=note)


def remove_correlation(
    store_path: Path,
    key: str,
    related_key: str,
    relation: Optional[str] = None,
) -> bool:
    """Remove a correlation entry.  If *relation* is None, remove all entries for *related_key*."""
    data = _load_correlations(store_path)
    entries = data.get(key, [])
    before = len(entries)

    if relation is None:
        entries = [e for e in entries if e["related_key"] != related_key]
    else:
        entries = [
            e for e in entries
            if not (e["related_key"] == related_key and e["relation"] == relation)
        ]

    if len(entries) == before:
        return False

    data[key] = entries
    if not data[key]:
        del data[key]
    _save_correlations(store_path, data)
    return True


def get_correlations(store_path: Path, key: str) -> List[CorrelationEntry]:
    """Return all correlations recorded for *key*."""
    data = _load_correlations(store_path)
    return [
        CorrelationEntry(
            related_key=e["related_key"],
            relation=e["relation"],
            note=e.get("note"),
        )
        for e in data.get(key, [])
    ]


def list_correlated_keys(store_path: Path) -> List[str]:
    """Return all keys that have at least one correlation entry."""
    data = _load_correlations(store_path)
    return sorted(data.keys())
