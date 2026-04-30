"""Tests for env_criticality module."""

from __future__ import annotations

import pytest

from envchain.env_criticality import (
    get_criticality,
    list_criticality,
    remove_criticality,
    set_criticality,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_criticality(store):
    result = set_criticality(store, "API_KEY", "high")
    assert result.ok
    assert result.level == "high"
    fetched = get_criticality(store, "API_KEY")
    assert fetched is not None
    assert fetched.level == "high"
    assert fetched.reason is None


def test_set_criticality_with_reason(store):
    result = set_criticality(store, "DB_PASS", "critical", reason="Production DB")
    assert result.ok
    assert result.reason == "Production DB"
    fetched = get_criticality(store, "DB_PASS")
    assert fetched.reason == "Production DB"


def test_get_missing_criticality_returns_none(store):
    result = get_criticality(store, "MISSING_KEY")
    assert result is None


def test_invalid_level_returns_error(store):
    result = set_criticality(store, "API_KEY", "extreme")
    assert not result.ok
    assert "extreme" in result.error


def test_overwrite_criticality(store):
    set_criticality(store, "TOKEN", "low")
    set_criticality(store, "TOKEN", "critical", reason="Updated")
    fetched = get_criticality(store, "TOKEN")
    assert fetched.level == "critical"
    assert fetched.reason == "Updated"


def test_remove_criticality_returns_true(store):
    set_criticality(store, "KEY", "medium")
    removed = remove_criticality(store, "KEY")
    assert removed is True
    assert get_criticality(store, "KEY") is None


def test_remove_missing_criticality_returns_false(store):
    removed = remove_criticality(store, "NONEXISTENT")
    assert removed is False


def test_list_criticality_empty(store):
    assert list_criticality(store) == []


def test_list_criticality_multiple(store):
    set_criticality(store, "A", "low")
    set_criticality(store, "B", "critical", reason="Important")
    set_criticality(store, "C", "medium")
    entries = list_criticality(store)
    assert len(entries) == 3
    keys = {e.key for e in entries}
    assert keys == {"A", "B", "C"}


def test_repr_ok(store):
    result = set_criticality(store, "X", "high", reason="test")
    assert "high" in repr(result)
    assert "X" in repr(result)


def test_repr_error(store):
    result = set_criticality(store, "X", "invalid")
    assert "error" in repr(result).lower()
