"""Track the origin/provenance of environment variables."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


def _provenance_path(store_path: str) -> Path:
    return Path(store_path).parent / "provenance.json"


def _load_provenance(store_path: str) -> dict:
    p = _provenance_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_provenance(store_path: str, data: dict) -> None:
    _provenance_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ProvenanceResult:
    key: str
    origin: str
    source_url: Optional[str]
    recorded_by: Optional[str]
    note: Optional[str]
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        if not self.ok:
            return f"ProvenanceResult(error={self.error!r})"
        return (
            f"ProvenanceResult(key={self.key!r}, origin={self.origin!r}, "
            f"source_url={self.source_url!r}, recorded_by={self.recorded_by!r})"
        )


VALID_ORIGINS = {"manual", "ci", "vault", "import", "generated", "external"}


def set_provenance(
    store_path: str,
    key: str,
    origin: str,
    source_url: Optional[str] = None,
    recorded_by: Optional[str] = None,
    note: Optional[str] = None,
) -> ProvenanceResult:
    if not key:
        return ProvenanceResult(key=key, origin=origin, source_url=source_url,
                                recorded_by=recorded_by, note=note,
                                ok=False, error="key must not be empty")
    if origin not in VALID_ORIGINS:
        return ProvenanceResult(key=key, origin=origin, source_url=source_url,
                                recorded_by=recorded_by, note=note,
                                ok=False, error=f"invalid origin '{origin}'; must be one of {sorted(VALID_ORIGINS)}")
    data = _load_provenance(store_path)
    data[key] = {
        "origin": origin,
        "source_url": source_url,
        "recorded_by": recorded_by,
        "note": note,
    }
    _save_provenance(store_path, data)
    return ProvenanceResult(key=key, origin=origin, source_url=source_url,
                            recorded_by=recorded_by, note=note, ok=True)


def get_provenance(store_path: str, key: str) -> Optional[ProvenanceResult]:
    data = _load_provenance(store_path)
    if key not in data:
        return None
    entry = data[key]
    return ProvenanceResult(
        key=key,
        origin=entry["origin"],
        source_url=entry.get("source_url"),
        recorded_by=entry.get("recorded_by"),
        note=entry.get("note"),
        ok=True,
    )


def remove_provenance(store_path: str, key: str) -> bool:
    data = _load_provenance(store_path)
    if key not in data:
        return False
    del data[key]
    _save_provenance(store_path, data)
    return True


def list_provenance(store_path: str) -> list[ProvenanceResult]:
    data = _load_provenance(store_path)
    results = []
    for key, entry in data.items():
        results.append(ProvenanceResult(
            key=key,
            origin=entry["origin"],
            source_url=entry.get("source_url"),
            recorded_by=entry.get("recorded_by"),
            note=entry.get("note"),
            ok=True,
        ))
    return results
