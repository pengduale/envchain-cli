import pytest
from pathlib import Path
from envchain.env_scope import (
    set_scope, get_scope, remove_scope, list_scopes, filter_keys_by_scope
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_set_and_get_scope(store):
    result = set_scope(store, "ci", ["API_KEY", "SECRET"])
    assert result.scope == "ci"
    assert result.action == "set"
    assert get_scope(store, "ci") == ["API_KEY", "SECRET"]


def test_get_missing_scope_returns_none(store):
    assert get_scope(store, "nonexistent") is None


def test_overwrite_scope(store):
    set_scope(store, "prod", ["A", "B"])
    set_scope(store, "prod", ["C"])
    assert get_scope(store, "prod") == ["C"]


def test_remove_scope_returns_true(store):
    set_scope(store, "dev", ["X"])
    assert remove_scope(store, "dev") is True
    assert get_scope(store, "dev") is None


def test_remove_missing_scope_returns_false(store):
    assert remove_scope(store, "ghost") is False


def test_list_scopes_empty(store):
    assert list_scopes(store) == {}


def test_list_scopes_multiple(store):
    set_scope(store, "ci", ["A"])
    set_scope(store, "prod", ["B", "C"])
    scopes = list_scopes(store)
    assert "ci" in scopes
    assert "prod" in scopes
    assert scopes["prod"] == ["B", "C"]


def test_filter_keys_by_scope_restricts(store):
    set_scope(store, "ci", ["A", "C"])
    result = filter_keys_by_scope(store, "ci", ["A", "B", "C", "D"])
    assert result == ["A", "C"]


def test_filter_keys_no_scope_returns_all(store):
    result = filter_keys_by_scope(store, "undefined", ["A", "B"])
    assert result == ["A", "B"]


def test_scope_file_created(store):
    set_scope(store, "x", ["K"])
    assert (Path(store) / ".scope_map.json").exists()
