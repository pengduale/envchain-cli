"""Tests for envchain.env_risk."""
import pytest
from pathlib import Path
from envchain.env_risk import (
    VALID_LEVELS,
    get_risk,
    list_risk,
    remove_risk,
    set_risk,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_set_and_get_risk(store):
    result = set_risk(store, "DB_PASSWORD", "high", "exposed in logs")
    assert result.ok
    assert result.level == "high"
    assert result.reason == "exposed in logs"

    fetched = get_risk(store, "DB_PASSWORD")
    assert fetched is not None
    assert fetched.level == "high"
    assert fetched.reason == "exposed in logs"


def test_get_missing_risk_returns_none(store):
    assert get_risk(store, "MISSING_KEY") is None


def test_invalid_level_returns_error(store):
    result = set_risk(store, "API_KEY", "extreme")
    assert not result.ok
    assert "invalid level" in result.error


def test_overwrite_risk(store):
    set_risk(store, "API_KEY", "low")
    set_risk(store, "API_KEY", "critical", "rotated secret")
    fetched = get_risk(store, "API_KEY")
    assert fetched.level == "critical"
    assert fetched.reason == "rotated secret"


def test_remove_risk_returns_true(store):
    set_risk(store, "TOKEN", "medium")
    assert remove_risk(store, "TOKEN") is True
    assert get_risk(store, "TOKEN") is None


def test_remove_missing_risk_returns_false(store):
    assert remove_risk(store, "NONEXISTENT") is False


def test_list_risk_empty(store):
    assert list_risk(store) == []


def test_list_risk_multiple(store):
    set_risk(store, "KEY_A", "low")
    set_risk(store, "KEY_B", "critical", "publicly visible")
    entries = list_risk(store)
    keys = {e.key for e in entries}
    assert keys == {"KEY_A", "KEY_B"}


def test_empty_key_returns_error(store):
    result = set_risk(store, "", "low")
    assert not result.ok
    assert "empty" in result.error


def test_all_valid_levels_accepted(store):
    for level in VALID_LEVELS:
        result = set_risk(store, f"KEY_{level.upper()}", level)
        assert result.ok, f"Expected ok for level {level!r}"


def test_risk_result_repr(store):
    r = set_risk(store, "X", "high")
    assert "high" in repr(r)
