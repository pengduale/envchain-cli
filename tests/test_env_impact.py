"""Tests for envchain.env_impact module."""

import pytest
from pathlib import Path
from envchain.env_impact import (
    set_impact,
    get_impact,
    remove_impact,
    list_by_level,
    VALID_LEVELS,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "store.json"


def test_set_and_get_impact(store):
    result = set_impact(store, "DB_PASSWORD", "critical")
    assert result.ok
    assert result.key == "DB_PASSWORD"
    assert result.level == "critical"
    assert result.reason is None

    fetched = get_impact(store, "DB_PASSWORD")
    assert fetched is not None
    assert fetched.level == "critical"


def test_set_impact_with_reason(store):
    result = set_impact(store, "API_KEY", "high", reason="Used in payment service")
    assert result.ok
    assert result.reason == "Used in payment service"

    fetched = get_impact(store, "API_KEY")
    assert fetched.reason == "Used in payment service"


def test_get_missing_impact_returns_none(store):
    assert get_impact(store, "NONEXISTENT") is None


def test_invalid_level_returns_error(store):
    result = set_impact(store, "FOO", "extreme")
    assert not result.ok
    assert "extreme" in result.error
    assert result.error is not None


def test_overwrite_impact(store):
    set_impact(store, "SECRET", "low")
    set_impact(store, "SECRET", "critical", reason="Escalated")
    fetched = get_impact(store, "SECRET")
    assert fetched.level == "critical"
    assert fetched.reason == "Escalated"


def test_remove_impact_returns_true(store):
    set_impact(store, "TOKEN", "medium")
    assert remove_impact(store, "TOKEN") is True
    assert get_impact(store, "TOKEN") is None


def test_remove_missing_impact_returns_false(store):
    assert remove_impact(store, "GHOST") is False


def test_list_by_level(store):
    set_impact(store, "DB_URL", "high")
    set_impact(store, "API_KEY", "high")
    set_impact(store, "LOG_LEVEL", "low")

    high_results = list_by_level(store, "high")
    keys = {r.key for r in high_results}
    assert keys == {"DB_URL", "API_KEY"}


def test_list_by_level_empty(store):
    assert list_by_level(store, "critical") == []


def test_valid_levels_constant():
    assert "low" in VALID_LEVELS
    assert "critical" in VALID_LEVELS
    assert len(VALID_LEVELS) == 4
