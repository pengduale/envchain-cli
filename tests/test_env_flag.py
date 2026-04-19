"""Tests for envchain.env_flag."""

import pytest
from pathlib import Path
from envchain.env_flag import (
    set_flag, get_flag, get_all_flags, remove_flag, list_flagged, VALID_FLAGS
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_flag(store):
    set_flag(store, "API_KEY", "sensitive")
    assert get_flag(store, "API_KEY", "sensitive") is True


def test_get_missing_flag_returns_none(store):
    assert get_flag(store, "API_KEY", "required") is None


def test_set_flag_false(store):
    set_flag(store, "DEBUG", "required", value=False)
    assert get_flag(store, "DEBUG", "required") is False


def test_overwrite_flag(store):
    set_flag(store, "TOKEN", "readonly", value=True)
    set_flag(store, "TOKEN", "readonly", value=False)
    assert get_flag(store, "TOKEN", "readonly") is False


def test_get_all_flags_empty(store):
    assert get_all_flags(store, "MISSING") == {}


def test_get_all_flags_multiple(store):
    set_flag(store, "SECRET", "sensitive")
    set_flag(store, "SECRET", "required")
    flags = get_all_flags(store, "SECRET")
    assert flags["sensitive"] is True
    assert flags["required"] is True


def test_remove_flag_returns_true(store):
    set_flag(store, "KEY", "deprecated")
    assert remove_flag(store, "KEY", "deprecated") is True
    assert get_flag(store, "KEY", "deprecated") is None


def test_remove_missing_flag_returns_false(store):
    assert remove_flag(store, "KEY", "sensitive") is False


def test_remove_cleans_up_empty_entry(store):
    set_flag(store, "SOLO", "readonly")
    remove_flag(store, "SOLO", "readonly")
    assert get_all_flags(store, "SOLO") == {}


def test_list_flagged(store):
    set_flag(store, "A", "sensitive")
    set_flag(store, "B", "sensitive")
    set_flag(store, "C", "required")
    result = list_flagged(store, "sensitive")
    assert set(result) == {"A", "B"}


def test_list_flagged_empty(store):
    assert list_flagged(store, "deprecated") == []


def test_invalid_flag_raises(store):
    with pytest.raises(ValueError, match="Unknown flag"):
        set_flag(store, "KEY", "nonexistent")


def test_invalid_flag_get_raises(store):
    with pytest.raises(ValueError):
        get_flag(store, "KEY", "bogus")


def test_flags_are_isolated_per_key(store):
    set_flag(store, "X", "sensitive")
    assert get_flag(store, "Y", "sensitive") is None
