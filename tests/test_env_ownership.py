"""Tests for envchain.env_ownership module."""
import pytest
from pathlib import Path
from envchain.env_ownership import (
    set_ownership,
    get_ownership,
    remove_ownership,
    list_owned_by,
    list_owned_by_team,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_ownership(store):
    result = set_ownership(store, "DB_PASSWORD", "alice")
    assert result.ok
    assert result.owner == "alice"
    fetched = get_ownership(store, "DB_PASSWORD")
    assert fetched is not None
    assert fetched.owner == "alice"
    assert fetched.team is None


def test_set_ownership_with_team(store):
    result = set_ownership(store, "API_KEY", "bob", team="backend")
    assert result.ok
    assert result.team == "backend"
    fetched = get_ownership(store, "API_KEY")
    assert fetched.team == "backend"


def test_get_missing_ownership_returns_none(store):
    result = get_ownership(store, "NONEXISTENT")
    assert result is None


def test_overwrite_ownership(store):
    set_ownership(store, "SECRET", "alice")
    set_ownership(store, "SECRET", "charlie", team="ops")
    fetched = get_ownership(store, "SECRET")
    assert fetched.owner == "charlie"
    assert fetched.team == "ops"


def test_remove_ownership_returns_true(store):
    set_ownership(store, "TOKEN", "alice")
    removed = remove_ownership(store, "TOKEN")
    assert removed is True
    assert get_ownership(store, "TOKEN") is None


def test_remove_missing_ownership_returns_false(store):
    removed = remove_ownership(store, "GHOST_KEY")
    assert removed is False


def test_list_owned_by(store):
    set_ownership(store, "KEY_A", "alice")
    set_ownership(store, "KEY_B", "bob")
    set_ownership(store, "KEY_C", "alice")
    keys = list_owned_by(store, "alice")
    assert set(keys) == {"KEY_A", "KEY_C"}


def test_list_owned_by_team(store):
    set_ownership(store, "KEY_X", "alice", team="frontend")
    set_ownership(store, "KEY_Y", "bob", team="backend")
    set_ownership(store, "KEY_Z", "carol", team="frontend")
    keys = list_owned_by_team(store, "frontend")
    assert set(keys) == {"KEY_X", "KEY_Z"}


def test_set_empty_key_fails(store):
    result = set_ownership(store, "", "alice")
    assert not result.ok
    assert "empty" in result.message.lower() or "not" in result.message.lower()


def test_set_empty_owner_fails(store):
    result = set_ownership(store, "MY_KEY", "")
    assert not result.ok


def test_repr(store):
    result = set_ownership(store, "REPR_KEY", "alice")
    assert "REPR_KEY" in repr(result)
    assert "alice" in repr(result)
