"""Tests for envchain.env_checksum."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from envchain.env_checksum import (
    ChecksumResult,
    list_checksums,
    record_checksum,
    remove_checksum,
    verify_checksum,
    _checksum_path,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    p = tmp_path / ".envchain.json"
    p.write_text(json.dumps({}))
    return p


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


# ---------------------------------------------------------------------------
# record_checksum
# ---------------------------------------------------------------------------

def test_record_checksum_returns_digest(store: Path) -> None:
    digest = record_checksum(store, "MY_KEY", "secret123")
    assert digest == _sha256("secret123")


def test_record_checksum_creates_file(store: Path) -> None:
    record_checksum(store, "MY_KEY", "secret123")
    assert _checksum_path(store).exists()


def test_record_checksum_persists_value(store: Path) -> None:
    record_checksum(store, "MY_KEY", "secret123")
    data = json.loads(_checksum_path(store).read_text())
    assert data["MY_KEY"] == _sha256("secret123")


def test_record_checksum_overwrites_previous(store: Path) -> None:
    record_checksum(store, "MY_KEY", "old_value")
    record_checksum(store, "MY_KEY", "new_value")
    data = json.loads(_checksum_path(store).read_text())
    assert data["MY_KEY"] == _sha256("new_value")


# ---------------------------------------------------------------------------
# verify_checksum
# ---------------------------------------------------------------------------

def test_verify_checksum_ok(store: Path) -> None:
    record_checksum(store, "API_KEY", "abc")
    result = verify_checksum(store, "API_KEY", "abc")
    assert isinstance(result, ChecksumResult)
    assert result.ok is True
    assert result.key == "API_KEY"


def test_verify_checksum_mismatch(store: Path) -> None:
    record_checksum(store, "API_KEY", "abc")
    result = verify_checksum(store, "API_KEY", "xyz")
    assert result.ok is False
    assert result.expected == _sha256("abc")
    assert result.actual == _sha256("xyz")


def test_verify_checksum_missing_key(store: Path) -> None:
    result = verify_checksum(store, "MISSING", "whatever")
    assert result.ok is False
    assert result.expected is None


# ---------------------------------------------------------------------------
# remove_checksum
# ---------------------------------------------------------------------------

def test_remove_checksum_returns_true_when_present(store: Path) -> None:
    record_checksum(store, "K", "v")
    assert remove_checksum(store, "K") is True


def test_remove_checksum_returns_false_when_absent(store: Path) -> None:
    assert remove_checksum(store, "NOPE") is False


def test_remove_checksum_deletes_entry(store: Path) -> None:
    record_checksum(store, "K", "v")
    remove_checksum(store, "K")
    data = json.loads(_checksum_path(store).read_text())
    assert "K" not in data


# ---------------------------------------------------------------------------
# list_checksums
# ---------------------------------------------------------------------------

def test_list_checksums_empty(store: Path) -> None:
    assert list_checksums(store) == {}


def test_list_checksums_returns_all(store: Path) -> None:
    record_checksum(store, "A", "val_a")
    record_checksum(store, "B", "val_b")
    result = list_checksums(store)
    assert set(result.keys()) == {"A", "B"}
    assert result["A"] == _sha256("val_a")
