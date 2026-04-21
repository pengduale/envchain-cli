"""Tests for envchain.env_checkpoint."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.env_checkpoint import (
    create_checkpoint,
    restore_checkpoint,
    list_checkpoints,
    delete_checkpoint,
)

PASS = "test-pass"


@pytest.fixture
def store(tmp_path):
    p = tmp_path / "store.json"
    return p


def _set(store, key, val):
    set_variable(store, PASS, key, val)


def test_create_checkpoint_returns_ok(store):
    _set(store, "FOO", "bar")
    result = create_checkpoint(store, PASS, "snap1")
    assert result.ok
    assert result.name == "snap1"
    assert result.keys_saved == 1


def test_create_checkpoint_multiple_keys(store):
    _set(store, "A", "1")
    _set(store, "B", "2")
    result = create_checkpoint(store, PASS, "multi")
    assert result.ok
    assert result.keys_saved == 2


def test_create_checkpoint_empty_store_fails(store):
    result = create_checkpoint(store, PASS, "empty")
    assert not result.ok
    assert result.error is not None


def test_restore_checkpoint_recovers_values(store):
    _set(store, "FOO", "original")
    create_checkpoint(store, PASS, "cp1")
    # overwrite value
    _set(store, "FOO", "changed")
    result = restore_checkpoint(store, PASS, "cp1", overwrite=True)
    assert result.ok
    assert result.keys_saved == 1
    from envchain.store import get_variable
    assert get_variable(store, PASS, "FOO") == "original"


def test_restore_skips_existing_without_overwrite(store):
    _set(store, "FOO", "v1")
    create_checkpoint(store, PASS, "cp2")
    _set(store, "FOO", "v2")
    result = restore_checkpoint(store, PASS, "cp2", overwrite=False)
    assert result.ok
    assert result.keys_saved == 0  # skipped because FOO already exists


def test_restore_missing_checkpoint_fails(store):
    result = restore_checkpoint(store, PASS, "nonexistent")
    assert not result.ok
    assert "not found" in result.error


def test_list_checkpoints_empty(store):
    items = list_checkpoints(store)
    assert items == []


def test_list_checkpoints_shows_created(store):
    _set(store, "K", "v")
    create_checkpoint(store, PASS, "alpha")
    create_checkpoint(store, PASS, "beta")
    items = list_checkpoints(store)
    names = [i["name"] for i in items]
    assert "alpha" in names
    assert "beta" in names


def test_delete_checkpoint_returns_true(store):
    _set(store, "X", "y")
    create_checkpoint(store, PASS, "todel")
    assert delete_checkpoint(store, "todel") is True


def test_delete_missing_checkpoint_returns_false(store):
    assert delete_checkpoint(store, "ghost") is False


def test_list_after_delete_is_empty(store):
    _set(store, "X", "y")
    create_checkpoint(store, PASS, "gone")
    delete_checkpoint(store, "gone")
    assert list_checkpoints(store) == []
