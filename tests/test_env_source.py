"""Tests for envchain.env_source module."""

import pytest
from pathlib import Path

from envchain.env_source import (
    set_source,
    get_source,
    remove_source,
    list_sources,
    VALID_SOURCES,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_set_and_get_source(store):
    result = set_source(store, "API_KEY", "manual")
    assert result.ok
    assert result.key == "API_KEY"
    assert result.source == "manual"

    fetched = get_source(store, "API_KEY")
    assert fetched is not None
    assert fetched.source == "manual"
    assert fetched.note is None


def test_set_source_with_note(store):
    result = set_source(store, "DB_PASS", "imported", note="from .env file")
    assert result.ok
    assert result.note == "from .env file"

    fetched = get_source(store, "DB_PASS")
    assert fetched.note == "from .env file"


def test_get_missing_source_returns_none(store):
    assert get_source(store, "NONEXISTENT") is None


def test_invalid_source_returns_error(store):
    result = set_source(store, "TOKEN", "unknown_origin")
    assert not result.ok
    assert "Invalid source" in result.error


def test_overwrite_source(store):
    set_source(store, "SECRET", "manual")
    set_source(store, "SECRET", "synced", note="synced from staging")

    fetched = get_source(store, "SECRET")
    assert fetched.source == "synced"
    assert fetched.note == "synced from staging"


def test_remove_source_returns_true(store):
    set_source(store, "KEY", "generated")
    assert remove_source(store, "KEY") is True
    assert get_source(store, "KEY") is None


def test_remove_missing_source_returns_false(store):
    assert remove_source(store, "GHOST_KEY") is False


def test_list_sources_empty(store):
    assert list_sources(store) == []


def test_list_sources_multiple(store):
    set_source(store, "A", "manual")
    set_source(store, "B", "imported")
    set_source(store, "C", "migrated")

    results = list_sources(store)
    keys = {r.key for r in results}
    assert keys == {"A", "B", "C"}


def test_all_valid_sources_accepted(store):
    for i, src in enumerate(VALID_SOURCES):
        result = set_source(store, f"KEY_{i}", src)
        assert result.ok, f"Expected source '{src}' to be valid"


def test_repr_ok(store):
    result = set_source(store, "X", "manual")
    assert "manual" in repr(result)
    assert "X" in repr(result)


def test_repr_error(store):
    result = set_source(store, "X", "bad_source")
    assert "error" in repr(result).lower()
