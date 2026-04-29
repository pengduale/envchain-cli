"""Attestation support: record and verify who attested a variable's value."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


def _attestation_path(store_path: Path) -> Path:
    return store_path.parent / "attestations.json"


def _load_attestations(store_path: Path) -> dict:
    p = _attestation_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_attestations(store_path: Path, data: dict) -> None:
    _attestation_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class AttestationResult:
    key: str
    attested_by: str
    attested_at: float
    note: Optional[str]
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        if self.ok:
            return f"<AttestationResult key={self.key!r} attested_by={self.attested_by!r}>"
        return f"<AttestationResult key={self.key!r} error={self.error!r}>"


def attest_variable(
    store_path: Path,
    key: str,
    attested_by: str,
    note: Optional[str] = None,
) -> AttestationResult:
    if not key:
        return AttestationResult(key=key, attested_by=attested_by, attested_at=0.0, note=note, ok=False, error="key must not be empty")
    if not attested_by:
        return AttestationResult(key=key, attested_by=attested_by, attested_at=0.0, note=note, ok=False, error="attested_by must not be empty")
    data = _load_attestations(store_path)
    ts = time.time()
    data[key] = {"attested_by": attested_by, "attested_at": ts, "note": note}
    _save_attestations(store_path, data)
    return AttestationResult(key=key, attested_by=attested_by, attested_at=ts, note=note, ok=True)


def get_attestation(store_path: Path, key: str) -> Optional[AttestationResult]:
    data = _load_attestations(store_path)
    entry = data.get(key)
    if entry is None:
        return None
    return AttestationResult(
        key=key,
        attested_by=entry["attested_by"],
        attested_at=entry["attested_at"],
        note=entry.get("note"),
        ok=True,
    )


def remove_attestation(store_path: Path, key: str) -> bool:
    data = _load_attestations(store_path)
    if key not in data:
        return False
    del data[key]
    _save_attestations(store_path, data)
    return True


def list_attestations(store_path: Path) -> list[AttestationResult]:
    data = _load_attestations(store_path)
    return [
        AttestationResult(
            key=k,
            attested_by=v["attested_by"],
            attested_at=v["attested_at"],
            note=v.get("note"),
            ok=True,
        )
        for k, v in data.items()
    ]
