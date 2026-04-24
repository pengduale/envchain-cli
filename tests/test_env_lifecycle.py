"""Tests for envchain.env_lifecycle."""

import pytest
from pathlib import Path

from envchain.env_lifecycle import (
    set_lifecycle,
    get_lifecycle,
    remove_lifecycle,
    list_by_state,
    list_all_lifecycle,
    VALID_STATES,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "store.json"


def test_set_and_get_lifecycle(store):
    result = set_lifecycle(store, "API_KEY", "active")
    assert result.ok
    assert result.state == "active"
    assert get_lifecycle(store, "API_KEY") == "active"


def test_get_missing_lifecycle_returns_none(store):
    assert get_lifecycle(store, "MISSING_KEY") is None


def test_overwrite_lifecycle(store):
    set_lifecycle(store, "DB_PASS", "draft")
    set_lifecycle(store, "DB_PASS", "active")
    assert get_lifecycle(store, "DB_PASS") == "active"


def test_invalid_state_raises(store):
    with pytest.raises(ValueError, match="Invalid state"):
        set_lifecycle(store, "KEY", "unknown")


def test_remove_lifecycle_returns_true(store):
    set_lifecycle(store, "KEY", "retired")
    assert remove_lifecycle(store, "KEY") is True
    assert get_lifecycle(store, "KEY") is None


def test_remove_missing_lifecycle_returns_false(store):
    assert remove_lifecycle(store, "NONEXISTENT") is False


def test_list_by_state(store):
    set_lifecycle(store, "A", "active")
    set_lifecycle(store, "B", "deprecated")
    set_lifecycle(store, "C", "active")
    active = list_by_state(store, "active")
    assert set(active) == {"A", "C"}


def test_list_by_state_empty(store):
    assert list_by_state(store, "retired") == []


def test_list_by_invalid_state_raises(store):
    with pytest.raises(ValueError, match="Invalid state"):
        list_by_state(store, "bogus")


def test_list_all_lifecycle(store):
    set_lifecycle(store, "X", "draft")
    set_lifecycle(store, "Y", "active")
    data = list_all_lifecycle(store)
    assert data == {"X": "draft", "Y": "active"}


def test_all_valid_states_accepted(store):
    for state in VALID_STATES:
        result = set_lifecycle(store, f"KEY_{state.upper()}", state)
        assert result.ok
        assert result.state == state
