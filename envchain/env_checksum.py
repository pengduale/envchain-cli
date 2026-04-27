"""Checksum tracking for stored environment variables.

Records and verifies SHA-256 checksums of plaintext values so that
out-of-band tampering or unexpected value changes can be detected.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _checksum_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_checksums.json"


def _load_checksums(store_path: Path) -> dict:
    p = _checksum_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_checksums(store_path: Path, data: dict) -> None:
    _checksum_path(store_path).write_text(json.dumps(data, indent=2))


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass
class ChecksumResult:
    key: str
    ok: bool
    expected: Optional[str]
    actual: Optional[str]

    def __repr__(self) -> str:  # pragma: no cover
        status = "OK" if self.ok else "MISMATCH"
        return f"<ChecksumResult {self.key} {status}>"


def record_checksum(store_path: Path, key: str, value: str) -> str:
    """Record a checksum for *key* based on its plaintext *value*.

    Returns the hex digest that was stored.
    """
    data = _load_checksums(store_path)
    digest = _sha256(value)
    data[key] = digest
    _save_checksums(store_path, data)
    return digest


def verify_checksum(store_path: Path, key: str, value: str) -> ChecksumResult:
    """Verify that *value* matches the recorded checksum for *key*."""
    data = _load_checksums(store_path)
    expected = data.get(key)
    actual = _sha256(value)
    return ChecksumResult(
        key=key,
        ok=(expected == actual),
        expected=expected,
        actual=actual,
    )


def remove_checksum(store_path: Path, key: str) -> bool:
    """Remove the stored checksum for *key*. Returns True if it existed."""
    data = _load_checksums(store_path)
    if key not in data:
        return False
    del data[key]
    _save_checksums(store_path, data)
    return True


def list_checksums(store_path: Path) -> dict[str, str]:
    """Return a mapping of key -> hex digest for all recorded checksums."""
    return _load_checksums(store_path)
