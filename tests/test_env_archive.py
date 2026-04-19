"""Tests for envchain.env_archive."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envchain.env_archive import (
    archive_variable,
    restore_variable,
    list_archived,
    purge_variable,
    _archive_path,
)


@pytest.fixture
def store(tmp_path) -> Path:
    p = tmp_path / "envchain.json"
    p.write_text(json.dumps({}))
    return p


def test_archive_creates_archive_file(store):
    archive_variable(store, "FOO", "enc_foo")
    assert _archive_path(store).exists()


def test_archive_stores_encrypted_value(store):
    archive_variable(store, "FOO", "enc_foo")
    data = json.loads(_archive_path(store).read_text())
    assert data["FOO"] == "enc_foo"


def test_list_archived_empty(store):
    assert list_archived(store) == []


def test_list_archived_after_add(store):
    archive_variable(store, "BAR", "enc_bar")
    archive_variable(store, "BAZ", "enc_baz")
    keys = list_archived(store)
    assert "BAR" in keys
    assert "BAZ" in keys


def test_restore_variable_returns_value(store):
    archive_variable(store, "KEY", "enc_val")
    result = restore_variable(store, "KEY")
    assert result.ok
    assert result.reason == "enc_val"


def test_restore_removes_from_archive(store):
    archive_variable(store, "KEY", "enc_val")
    restore_variable(store, "KEY")
    assert "KEY" not in list_archived(store)


def test_restore_missing_key_fails(store):
    result = restore_variable(store, "MISSING")
    assert not result.ok
    assert "not in archive" in result.reason


def test_purge_removes_key(store):
    archive_variable(store, "DEL", "enc_del")
    result = purge_variable(store, "DEL")
    assert result.ok
    assert "DEL" not in list_archived(store)


def test_purge_missing_key_fails(store):
    result = purge_variable(store, "NOPE")
    assert not result.ok


def test_archive_result_repr(store):
    r = archive_variable(store, "X", "v")
    assert "archived" in repr(r)
    assert "X" in repr(r)
