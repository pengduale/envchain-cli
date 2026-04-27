"""Tests for envchain.env_readonly."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_readonly import (
    set_readonly,
    is_readonly,
    remove_readonly,
    list_readonly_keys,
    ReadonlyResult,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / ".envchain.json"
    store_file.write_text("{}")
    return store_file


def test_set_readonly_returns_result(store):
    result = set_readonly(store, "API_KEY")
    assert isinstance(result, ReadonlyResult)
    assert result.ok is True
    assert result.locked is True
    assert result.key == "API_KEY"


def test_is_readonly_after_set(store):
    set_readonly(store, "API_KEY")
    assert is_readonly(store, "API_KEY") is True


def test_is_readonly_default_false(store):
    assert is_readonly(store, "MISSING_KEY") is False


def test_set_readonly_false_unlocks(store):
    set_readonly(store, "API_KEY", locked=True)
    set_readonly(store, "API_KEY", locked=False)
    assert is_readonly(store, "API_KEY") is False


def test_remove_readonly_returns_ok(store):
    set_readonly(store, "SECRET")
    result = remove_readonly(store, "SECRET")
    assert result.ok is True
    assert result.locked is False


def test_remove_readonly_missing_key(store):
    result = remove_readonly(store, "NONEXISTENT")
    assert result.ok is False


def test_list_readonly_keys_empty(store):
    assert list_readonly_keys(store) == []


def test_list_readonly_keys_multiple(store):
    set_readonly(store, "KEY_A")
    set_readonly(store, "KEY_B")
    keys = list_readonly_keys(store)
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_list_readonly_excludes_unlocked(store):
    set_readonly(store, "KEY_A", locked=True)
    set_readonly(store, "KEY_B", locked=False)
    keys = list_readonly_keys(store)
    assert "KEY_A" in keys
    assert "KEY_B" not in keys


def test_repr_locked(store):
    result = set_readonly(store, "TOKEN")
    assert "locked" in repr(result)
    assert "TOKEN" in repr(result)
