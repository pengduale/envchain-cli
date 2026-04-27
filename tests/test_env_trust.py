"""Tests for envchain.env_trust module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_trust import (
    TrustResult,
    get_trust,
    list_trust,
    remove_trust,
    set_trust,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "store.json"


def test_set_and_get_trust(store):
    result = set_trust(store, "API_KEY", "high")
    assert isinstance(result, TrustResult)
    assert result.ok is True
    assert result.key == "API_KEY"
    assert result.level == "high"
    assert get_trust(store, "API_KEY") == "high"


def test_get_missing_trust_returns_none(store):
    assert get_trust(store, "MISSING") is None


def test_overwrite_trust(store):
    set_trust(store, "DB_PASS", "low")
    set_trust(store, "DB_PASS", "verified")
    assert get_trust(store, "DB_PASS") == "verified"


def test_invalid_trust_level_raises(store):
    with pytest.raises(ValueError, match="Invalid trust level"):
        set_trust(store, "KEY", "super-trusted")


def test_remove_trust_returns_true(store):
    set_trust(store, "TOKEN", "medium")
    assert remove_trust(store, "TOKEN") is True
    assert get_trust(store, "TOKEN") is None


def test_remove_missing_trust_returns_false(store):
    assert remove_trust(store, "NONEXISTENT") is False


def test_list_trust_empty(store):
    assert list_trust(store) == {}


def test_list_trust_multiple_keys(store):
    set_trust(store, "A", "low")
    set_trust(store, "B", "high")
    set_trust(store, "C", "verified")
    mapping = list_trust(store)
    assert mapping == {"A": "low", "B": "high", "C": "verified"}


def test_trust_result_repr(store):
    result = set_trust(store, "X", "untrusted")
    assert "X" in repr(result)
    assert "untrusted" in repr(result)


def test_all_valid_levels_accepted(store):
    from envchain.env_trust import VALID_LEVELS
    for level in VALID_LEVELS:
        result = set_trust(store, f"KEY_{level.upper()}", level)
        assert result.ok is True
