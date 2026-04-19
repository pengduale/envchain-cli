"""Tests for envchain.env_description."""

import pytest
from pathlib import Path
from envchain.env_description import (
    set_description,
    get_description,
    remove_description,
    list_descriptions,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_set_and_get_description(store):
    set_description(store, "API_KEY", "The primary API key")
    result = get_description(store, "API_KEY")
    assert result == "The primary API key"


def test_get_missing_description_returns_none(store):
    assert get_description(store, "MISSING") is None


def test_overwrite_description(store):
    set_description(store, "DB_URL", "old")
    set_description(store, "DB_URL", "new")
    assert get_description(store, "DB_URL") == "new"


def test_remove_description_returns_true(store):
    set_description(store, "TOKEN", "some token")
    assert remove_description(store, "TOKEN") is True
    assert get_description(store, "TOKEN") is None


def test_remove_missing_returns_false(store):
    assert remove_description(store, "GHOST") is False


def test_list_descriptions_empty(store):
    assert list_descriptions(store) == {}


def test_list_descriptions_multiple(store):
    set_description(store, "A", "alpha")
    set_description(store, "B", "beta")
    result = list_descriptions(store)
    assert result == {"A": "alpha", "B": "beta"}


def test_set_empty_key_raises(store):
    with pytest.raises(ValueError):
        set_description(store, "", "some desc")


def test_result_repr(store):
    r = set_description(store, "X", "desc")
    assert "X" in repr(r)
    assert "ok=True" in repr(r)


def test_descriptions_file_created(store):
    set_description(store, "KEY", "value")
    p = Path(store) / ".descriptions.json"
    assert p.exists()
