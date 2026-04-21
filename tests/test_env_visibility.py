"""Tests for envchain.env_visibility."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_visibility import (
    VALID_LEVELS,
    get_visibility,
    list_visibility,
    remove_visibility,
    set_visibility,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    store_file = tmp_path / ".envchain.json"
    store_file.write_text("{}")
    return store_file


def test_set_and_get_visibility(store):
    result = set_visibility(store, "API_KEY", "private")
    assert result.ok
    assert result.level == "private"
    assert get_visibility(store, "API_KEY") == "private"


def test_get_missing_visibility_returns_none(store):
    assert get_visibility(store, "MISSING_KEY") is None


def test_overwrite_visibility(store):
    set_visibility(store, "TOKEN", "public")
    set_visibility(store, "TOKEN", "secret")
    assert get_visibility(store, "TOKEN") == "secret"


def test_remove_visibility_returns_true(store):
    set_visibility(store, "DB_PASS", "secret")
    assert remove_visibility(store, "DB_PASS") is True
    assert get_visibility(store, "DB_PASS") is None


def test_remove_missing_visibility_returns_false(store):
    assert remove_visibility(store, "NONEXISTENT") is False


def test_list_visibility_empty(store):
    assert list_visibility(store) == {}


def test_list_visibility_multiple(store):
    set_visibility(store, "KEY_A", "public")
    set_visibility(store, "KEY_B", "internal")
    set_visibility(store, "KEY_C", "secret")
    result = list_visibility(store)
    assert result == {"KEY_A": "public", "KEY_B": "internal", "KEY_C": "secret"}


def test_invalid_level_raises(store):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        set_visibility(store, "KEY", "unknown")


def test_all_valid_levels_accepted(store):
    for level in VALID_LEVELS:
        result = set_visibility(store, f"KEY_{level.upper()}", level)
        assert result.ok
        assert result.level == level


def test_visibility_repr(store):
    result = set_visibility(store, "MY_KEY", "internal")
    assert "MY_KEY" in repr(result)
    assert "internal" in repr(result)
