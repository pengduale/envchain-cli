"""Tests for envchain.env_exposure module."""

import pytest
from pathlib import Path

from envchain.env_exposure import (
    set_exposure,
    get_exposure,
    remove_exposure,
    list_exposure,
    ExposureResult,
    VALID_LEVELS,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "envchain.enc"
    store_file.write_text("{}")
    return store_file


def test_set_and_get_exposure(store):
    result = set_exposure(store, "API_KEY", "high", surfaces=["logs", "network"])
    assert result.ok
    assert result.key == "API_KEY"
    assert result.level == "high"
    assert "logs" in result.surfaces


def test_get_missing_exposure_returns_none(store):
    assert get_exposure(store, "MISSING_KEY") is None


def test_set_exposure_with_note(store):
    result = set_exposure(store, "DB_PASS", "critical", note="Exposed via CI logs")
    assert result.ok
    assert result.note == "Exposed via CI logs"


def test_invalid_level_returns_error(store):
    result = set_exposure(store, "TOKEN", "extreme")
    assert not result.ok
    assert "extreme" in result.error


def test_empty_key_returns_error(store):
    result = set_exposure(store, "", "low")
    assert not result.ok
    assert "empty" in result.error.lower()


def test_overwrite_exposure(store):
    set_exposure(store, "SECRET", "low")
    set_exposure(store, "SECRET", "critical", surfaces=["public-api"])
    result = get_exposure(store, "SECRET")
    assert result.level == "critical"
    assert "public-api" in result.surfaces


def test_remove_exposure_returns_true(store):
    set_exposure(store, "KEY", "medium")
    assert remove_exposure(store, "KEY") is True
    assert get_exposure(store, "KEY") is None


def test_remove_missing_returns_false(store):
    assert remove_exposure(store, "GHOST_KEY") is False


def test_list_exposure_sorted_by_severity(store):
    set_exposure(store, "A", "low")
    set_exposure(store, "B", "critical")
    set_exposure(store, "C", "medium")
    results = list_exposure(store)
    levels = [r.level for r in results]
    assert levels == sorted(levels, key=lambda l: VALID_LEVELS.index(l), reverse=True)


def test_list_exposure_empty_store(store):
    assert list_exposure(store) == []


def test_exposure_repr_ok(store):
    result = set_exposure(store, "X", "none")
    assert "X" in repr(result)
    assert "none" in repr(result)


def test_exposure_repr_error(store):
    result = set_exposure(store, "", "low")
    assert "error" in repr(result).lower()


def test_set_all_valid_levels(store):
    for i, level in enumerate(VALID_LEVELS):
        key = f"KEY_{i}"
        result = set_exposure(store, key, level)
        assert result.ok
        assert result.level == level
