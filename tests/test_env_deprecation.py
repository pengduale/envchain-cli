"""Tests for envchain.env_deprecation."""

import pytest
from pathlib import Path

from envchain.env_deprecation import (
    mark_deprecated,
    get_deprecation,
    remove_deprecation,
    list_deprecated,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path


def test_mark_deprecated_returns_result(store):
    result = mark_deprecated(store, "OLD_KEY", "use NEW_KEY instead", replacement="NEW_KEY")
    assert result.ok is True
    assert result.key == "OLD_KEY"
    assert result.reason == "use NEW_KEY instead"
    assert result.replacement == "NEW_KEY"


def test_mark_deprecated_no_replacement(store):
    result = mark_deprecated(store, "LEGACY_TOKEN", "no longer needed")
    assert result.replacement is None
    assert result.ok is True


def test_get_deprecation_after_mark(store):
    mark_deprecated(store, "OLD_KEY", "outdated", replacement="NEW_KEY")
    result = get_deprecation(store, "OLD_KEY")
    assert result is not None
    assert result.key == "OLD_KEY"
    assert result.replacement == "NEW_KEY"


def test_get_deprecation_missing_returns_none(store):
    result = get_deprecation(store, "NONEXISTENT")
    assert result is None


def test_overwrite_deprecation(store):
    mark_deprecated(store, "OLD_KEY", "first reason")
    mark_deprecated(store, "OLD_KEY", "updated reason", replacement="BETTER_KEY")
    result = get_deprecation(store, "OLD_KEY")
    assert result.reason == "updated reason"
    assert result.replacement == "BETTER_KEY"


def test_remove_deprecation_returns_true(store):
    mark_deprecated(store, "OLD_KEY", "outdated")
    removed = remove_deprecation(store, "OLD_KEY")
    assert removed is True
    assert get_deprecation(store, "OLD_KEY") is None


def test_remove_deprecation_missing_returns_false(store):
    removed = remove_deprecation(store, "NEVER_SET")
    assert removed is False


def test_list_deprecated_empty(store):
    results = list_deprecated(store)
    assert results == []


def test_list_deprecated_multiple(store):
    mark_deprecated(store, "KEY_A", "reason A")
    mark_deprecated(store, "KEY_B", "reason B", replacement="KEY_C")
    results = list_deprecated(store)
    keys = {r.key for r in results}
    assert "KEY_A" in keys
    assert "KEY_B" in keys
    assert len(results) == 2


def test_mark_deprecated_empty_key_raises(store):
    with pytest.raises(ValueError, match="key"):
        mark_deprecated(store, "", "some reason")


def test_mark_deprecated_empty_reason_raises(store):
    with pytest.raises(ValueError, match="reason"):
        mark_deprecated(store, "OLD_KEY", "")


def test_repr_includes_key_and_reason(store):
    result = mark_deprecated(store, "OLD_KEY", "legacy", replacement="NEW_KEY")
    r = repr(result)
    assert "OLD_KEY" in r
    assert "NEW_KEY" in r
    assert "legacy" in r
