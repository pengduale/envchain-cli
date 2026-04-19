"""Tests for envchain.env_clone."""
import pytest
from pathlib import Path
from envchain.env_clone import clone_profile, CloneResult
from envchain.profile import set_profile_variable, get_profile_variable

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def _set(store, profile, key, value):
    set_profile_variable(store, profile, key, value, PASS)


def _get(store, profile, key):
    return get_profile_variable(store, profile, key, PASS)


def test_clone_basic(store):
    _set(store, "src", "KEY1", "val1")
    _set(store, "src", "KEY2", "val2")
    result = clone_profile(store, "src", "dst", PASS)
    assert result.copied == 2
    assert result.skipped == 0
    assert result.overwritten == 0
    assert _get(store, "dst", "KEY1") == "val1"
    assert _get(store, "dst", "KEY2") == "val2"


def test_clone_skips_existing_without_overwrite(store):
    _set(store, "src", "KEY1", "new")
    _set(store, "dst", "KEY1", "old")
    result = clone_profile(store, "src", "dst", PASS)
    assert result.skipped == 1
    assert result.copied == 0
    assert _get(store, "dst", "KEY1") == "old"


def test_clone_overwrites_when_flag_set(store):
    _set(store, "src", "KEY1", "new")
    _set(store, "dst", "KEY1", "old")
    result = clone_profile(store, "src", "dst", PASS, overwrite=True)
    assert result.overwritten == 1
    assert _get(store, "dst", "KEY1") == "new"


def test_clone_with_prefix_filter(store):
    _set(store, "src", "APP_KEY", "a")
    _set(store, "src", "DB_KEY", "b")
    result = clone_profile(store, "src", "dst", PASS, prefix="APP_")
    assert result.copied == 1
    assert _get(store, "dst", "APP_KEY") == "a"
    assert _get(store, "dst", "DB_KEY") is None


def test_clone_empty_source(store):
    result = clone_profile(store, "empty", "dst", PASS)
    assert result.copied == 0
    assert result.skipped == 0


def test_clone_result_repr(store):
    _set(store, "src", "X", "1")
    result = clone_profile(store, "src", "dst", PASS)
    r = repr(result)
    assert "src" in r
    assert "dst" in r
