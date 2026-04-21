"""Tests for envchain.env_dependency."""
from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_dependency import (
    add_dependency,
    check_dependencies,
    get_dependencies,
    list_all_dependencies,
    remove_dependency,
)


@pytest.fixture
def store(tmp_path) -> Path:
    store_file = tmp_path / ".envchain" / "store.json"
    store_file.parent.mkdir(parents=True)
    store_file.write_text("{}")
    return store_file


def test_add_dependency_returns_result(store):
    result = add_dependency(store, "DB_URL", "DB_HOST")
    assert result.ok
    assert "DB_HOST" in result.depends_on


def test_add_dependency_no_duplicates(store):
    add_dependency(store, "DB_URL", "DB_HOST")
    result = add_dependency(store, "DB_URL", "DB_HOST")
    assert result.depends_on.count("DB_HOST") == 1


def test_add_multiple_dependencies(store):
    add_dependency(store, "DB_URL", "DB_HOST")
    add_dependency(store, "DB_URL", "DB_PORT")
    deps = get_dependencies(store, "DB_URL")
    assert "DB_HOST" in deps
    assert "DB_PORT" in deps


def test_get_dependencies_missing_key_returns_empty(store):
    assert get_dependencies(store, "NONEXISTENT") == []


def test_remove_dependency_returns_true(store):
    add_dependency(store, "DB_URL", "DB_HOST")
    removed = remove_dependency(store, "DB_URL", "DB_HOST")
    assert removed is True
    assert get_dependencies(store, "DB_URL") == []


def test_remove_dependency_missing_returns_false(store):
    removed = remove_dependency(store, "DB_URL", "DB_HOST")
    assert removed is False


def test_list_all_dependencies_empty(store):
    assert list_all_dependencies(store) == {}


def test_list_all_dependencies_multiple_keys(store):
    add_dependency(store, "A", "B")
    add_dependency(store, "C", "D")
    all_deps = list_all_dependencies(store)
    assert "A" in all_deps
    assert "C" in all_deps


def test_check_dependencies_all_present(store):
    add_dependency(store, "DB_URL", "DB_HOST")
    result = check_dependencies(store, "DB_URL", ["DB_HOST", "DB_PORT"])
    assert result.ok


def test_check_dependencies_missing(store):
    add_dependency(store, "DB_URL", "DB_HOST")
    add_dependency(store, "DB_URL", "DB_PORT")
    result = check_dependencies(store, "DB_URL", ["DB_HOST"])
    assert not result.ok
    assert "DB_PORT" in result.message


def test_check_dependencies_no_deps_always_ok(store):
    result = check_dependencies(store, "STANDALONE", [])
    assert result.ok


def test_add_dependency_empty_key_raises(store):
    with pytest.raises(ValueError):
        add_dependency(store, "", "DB_HOST")


def test_add_dependency_empty_dep_raises(store):
    with pytest.raises(ValueError):
        add_dependency(store, "DB_URL", "")
