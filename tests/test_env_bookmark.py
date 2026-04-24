"""Tests for envchain.env_bookmark."""

import pytest
from pathlib import Path

from envchain.env_bookmark import (
    add_bookmark,
    get_bookmark,
    remove_bookmark,
    list_bookmarks,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    store_path = tmp_path / "store"
    store_path.mkdir()
    return store_path


def test_add_and_get_bookmark(store):
    result = add_bookmark(store, "my-db", "DB_URL", profile="production")
    assert result.ok
    entry = get_bookmark(store, "my-db")
    assert entry is not None
    assert entry["key"] == "DB_URL"
    assert entry["profile"] == "production"


def test_add_bookmark_default_profile(store):
    result = add_bookmark(store, "api", "API_KEY")
    assert result.ok
    entry = get_bookmark(store, "api")
    assert entry["profile"] == "default"


def test_get_missing_bookmark_returns_none(store):
    assert get_bookmark(store, "nonexistent") is None


def test_overwrite_bookmark(store):
    add_bookmark(store, "ref", "OLD_KEY", profile="dev")
    add_bookmark(store, "ref", "NEW_KEY", profile="prod")
    entry = get_bookmark(store, "ref")
    assert entry["key"] == "NEW_KEY"
    assert entry["profile"] == "prod"


def test_remove_bookmark_returns_true(store):
    add_bookmark(store, "temp", "TEMP_KEY")
    assert remove_bookmark(store, "temp") is True
    assert get_bookmark(store, "temp") is None


def test_remove_missing_bookmark_returns_false(store):
    assert remove_bookmark(store, "ghost") is False


def test_list_bookmarks_empty(store):
    assert list_bookmarks(store) == []


def test_list_bookmarks_multiple(store):
    add_bookmark(store, "z-last", "Z_KEY", profile="dev")
    add_bookmark(store, "a-first", "A_KEY", profile="prod")
    items = list_bookmarks(store)
    assert len(items) == 2
    assert items[0]["name"] == "a-first"
    assert items[1]["name"] == "z-last"


def test_add_bookmark_empty_name_fails(store):
    result = add_bookmark(store, "", "SOME_KEY")
    assert not result.ok
    assert "empty" in result.message.lower()


def test_add_bookmark_empty_key_fails(store):
    result = add_bookmark(store, "mybookmark", "")
    assert not result.ok
    assert "empty" in result.message.lower()


def test_repr_contains_name_and_key(store):
    result = add_bookmark(store, "check", "CHECK_KEY", profile="staging")
    r = repr(result)
    assert "check" in r
    assert "CHECK_KEY" in r
