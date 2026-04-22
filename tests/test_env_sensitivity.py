"""Tests for envchain.env_sensitivity."""

from __future__ import annotations

import pytest

from envchain.env_sensitivity import (
    VALID_LEVELS,
    get_keys_by_level,
    get_sensitivity,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_set_and_get_sensitivity(store):
    result = set_sensitivity(store, "DB_PASSWORD", "critical")
    assert result.ok
    assert result.key == "DB_PASSWORD"
    assert result.level == "critical"
    assert get_sensitivity(store, "DB_PASSWORD") == "critical"


def test_get_missing_sensitivity_returns_none(store):
    assert get_sensitivity(store, "MISSING_KEY") is None


def test_overwrite_sensitivity(store):
    set_sensitivity(store, "API_KEY", "low")
    set_sensitivity(store, "API_KEY", "high")
    assert get_sensitivity(store, "API_KEY") == "high"


def test_invalid_level_raises(store):
    with pytest.raises(ValueError, match="Invalid sensitivity level"):
        set_sensitivity(store, "API_KEY", "ultra")


def test_remove_sensitivity_returns_true(store):
    set_sensitivity(store, "TOKEN", "medium")
    assert remove_sensitivity(store, "TOKEN") is True
    assert get_sensitivity(store, "TOKEN") is None


def test_remove_missing_returns_false(store):
    assert remove_sensitivity(store, "NONEXISTENT") is False


def test_list_sensitivity_empty(store):
    assert list_sensitivity(store) == {}


def test_list_sensitivity_multiple(store):
    set_sensitivity(store, "A", "low")
    set_sensitivity(store, "B", "critical")
    data = list_sensitivity(store)
    assert data["A"] == "low"
    assert data["B"] == "critical"


def test_get_keys_by_level(store):
    set_sensitivity(store, "X", "high")
    set_sensitivity(store, "Y", "high")
    set_sensitivity(store, "Z", "low")
    keys = get_keys_by_level(store, "high")
    assert set(keys) == {"X", "Y"}


def test_get_keys_by_level_empty(store):
    assert get_keys_by_level(store, "critical") == []


def test_all_valid_levels_accepted(store):
    for level in VALID_LEVELS:
        result = set_sensitivity(store, f"KEY_{level.upper()}", level)
        assert result.ok
