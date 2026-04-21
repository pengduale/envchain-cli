"""Tests for envchain.env_namespace."""

import pytest
from pathlib import Path
from envchain.env_namespace import (
    assign_namespace,
    get_namespace,
    remove_namespace,
    list_keys_in_namespace,
    list_namespaces,
    NamespaceResult,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / ".envchain" / "store.json"
    store_file.parent.mkdir(parents=True, exist_ok=True)
    store_file.write_text("{}")
    return store_file


def test_assign_namespace_returns_result(store):
    result = assign_namespace(store, "API_KEY", "auth")
    assert isinstance(result, NamespaceResult)
    assert result.ok is True
    assert result.namespace == "auth"
    assert result.key == "API_KEY"
    assert result.action == "assign"


def test_get_namespace_after_assign(store):
    assign_namespace(store, "DB_URL", "database")
    assert get_namespace(store, "DB_URL") == "database"


def test_get_missing_namespace_returns_none(store):
    assert get_namespace(store, "NONEXISTENT") is None


def test_overwrite_namespace(store):
    assign_namespace(store, "SECRET", "old-ns")
    assign_namespace(store, "SECRET", "new-ns")
    assert get_namespace(store, "SECRET") == "new-ns"


def test_remove_namespace_returns_true(store):
    assign_namespace(store, "TOKEN", "auth")
    result = remove_namespace(store, "TOKEN")
    assert result is True
    assert get_namespace(store, "TOKEN") is None


def test_remove_missing_namespace_returns_false(store):
    assert remove_namespace(store, "GHOST") is False


def test_list_keys_in_namespace(store):
    assign_namespace(store, "API_KEY", "auth")
    assign_namespace(store, "API_SECRET", "auth")
    assign_namespace(store, "DB_URL", "database")
    keys = list_keys_in_namespace(store, "auth")
    assert set(keys) == {"API_KEY", "API_SECRET"}


def test_list_keys_in_empty_namespace(store):
    assign_namespace(store, "FOO", "other")
    assert list_keys_in_namespace(store, "missing-ns") == []


def test_list_namespaces_returns_sorted_unique(store):
    assign_namespace(store, "A", "zebra")
    assign_namespace(store, "B", "alpha")
    assign_namespace(store, "C", "alpha")
    ns = list_namespaces(store)
    assert ns == ["alpha", "zebra"]


def test_list_namespaces_empty_store(store):
    assert list_namespaces(store) == []


def test_empty_namespace_raises(store):
    with pytest.raises(ValueError, match="Namespace must not be empty"):
        assign_namespace(store, "KEY", "   ")


def test_namespace_result_repr(store):
    result = assign_namespace(store, "X", "myns")
    assert "myns" in repr(result)
    assert "X" in repr(result)
