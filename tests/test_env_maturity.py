"""Tests for envchain.env_maturity."""
import pytest
from pathlib import Path

from envchain.env_maturity import (
    VALID_LEVELS,
    MaturityResult,
    filter_by_level,
    get_maturity,
    list_maturity,
    remove_maturity,
    set_maturity,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "store.json"


def test_set_and_get_maturity(store):
    result = set_maturity(store, "API_KEY", "stable")
    assert result.key == "API_KEY"
    assert result.level == "stable"
    assert result.ok is True

    fetched = get_maturity(store, "API_KEY")
    assert fetched is not None
    assert fetched.level == "stable"


def test_get_missing_maturity_returns_none(store):
    assert get_maturity(store, "MISSING_KEY") is None


def test_set_maturity_with_note(store):
    set_maturity(store, "DB_PASS", "beta", note="Pending review")
    result = get_maturity(store, "DB_PASS")
    assert result.note == "Pending review"


def test_overwrite_maturity(store):
    set_maturity(store, "TOKEN", "experimental")
    set_maturity(store, "TOKEN", "stable", note="Promoted")
    result = get_maturity(store, "TOKEN")
    assert result.level == "stable"
    assert result.note == "Promoted"


def test_invalid_level_raises(store):
    with pytest.raises(ValueError, match="Invalid maturity level"):
        set_maturity(store, "KEY", "unknown")


def test_remove_maturity_returns_true(store):
    set_maturity(store, "KEY", "deprecated")
    assert remove_maturity(store, "KEY") is True
    assert get_maturity(store, "KEY") is None


def test_remove_missing_maturity_returns_false(store):
    assert remove_maturity(store, "GHOST") is False


def test_list_maturity_empty(store):
    assert list_maturity(store) == []


def test_list_maturity_multiple(store):
    set_maturity(store, "A", "stable")
    set_maturity(store, "B", "beta")
    set_maturity(store, "C", "experimental")
    results = list_maturity(store)
    assert len(results) == 3
    keys = {r.key for r in results}
    assert keys == {"A", "B", "C"}


def test_filter_by_level(store):
    set_maturity(store, "X", "stable")
    set_maturity(store, "Y", "stable")
    set_maturity(store, "Z", "beta")
    stable = filter_by_level(store, "stable")
    assert len(stable) == 2
    assert all(r.level == "stable" for r in stable)


def test_all_valid_levels_accepted(store):
    for i, level in enumerate(VALID_LEVELS):
        set_maturity(store, f"KEY_{i}", level)
        result = get_maturity(store, f"KEY_{i}")
        assert result.level == level


def test_repr_with_note(store):
    result = set_maturity(store, "MY_KEY", "retired", note="End of life")
    r = repr(result)
    assert "MY_KEY" in r
    assert "retired" in r
    assert "End of life" in r
