"""Tests for envchain.env_group."""

import pytest
from pathlib import Path
from envchain.env_group import (
    create_group,
    get_group,
    delete_group,
    list_groups,
    add_key_to_group,
    remove_key_from_group,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_create_group_basic(store):
    result = create_group(store, "backend", ["DB_URL", "SECRET_KEY"])
    assert result.success
    assert result.group == "backend"
    assert "DB_URL" in result.keys


def test_get_group_returns_keys(store):
    create_group(store, "backend", ["DB_URL", "SECRET_KEY"])
    keys = get_group(store, "backend")
    assert keys == ["DB_URL", "SECRET_KEY"]


def test_get_group_missing_returns_none(store):
    assert get_group(store, "nonexistent") is None


def test_create_group_empty_name_fails(store):
    result = create_group(store, "", ["KEY"])
    assert not result.success


def test_create_group_empty_keys_fails(store):
    result = create_group(store, "grp", [])
    assert not result.success


def test_delete_group_returns_true(store):
    create_group(store, "grp", ["A"])
    assert delete_group(store, "grp") is True
    assert get_group(store, "grp") is None


def test_delete_missing_group_returns_false(store):
    assert delete_group(store, "ghost") is False


def test_list_groups_empty(store):
    assert list_groups(store) == []


def test_list_groups_multiple(store):
    create_group(store, "a", ["X"])
    create_group(store, "b", ["Y"])
    groups = list_groups(store)
    assert set(groups) == {"a", "b"}


def test_add_key_to_group(store):
    create_group(store, "grp", ["A"])
    result = add_key_to_group(store, "grp", "B")
    assert "B" in result.keys
    assert "A" in result.keys


def test_add_key_no_duplicate(store):
    create_group(store, "grp", ["A"])
    add_key_to_group(store, "grp", "A")
    assert get_group(store, "grp").count("A") == 1


def test_remove_key_from_group(store):
    create_group(store, "grp", ["A", "B"])
    result = remove_key_from_group(store, "grp", "A")
    assert result.success
    assert "A" not in result.keys


def test_remove_missing_key_fails(store):
    create_group(store, "grp", ["A"])
    result = remove_key_from_group(store, "grp", "Z")
    assert not result.success
