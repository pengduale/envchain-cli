"""Tests for envchain.env_rename."""
import pytest
from pathlib import Path
from envchain.store import set_variable, get_variable
from envchain.profile import set_profile_variable, get_profile_variable
from envchain.env_rename import rename_variable, rename_all_profiles

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return tmp_path / ".envchain"


def test_rename_basic(store):
    set_variable(store, "OLD_KEY", "hello", PASS)
    r = rename_variable(store, "OLD_KEY", "NEW_KEY", PASS)
    assert r.success
    assert get_variable(store, "NEW_KEY", PASS) == "hello"
    assert get_variable(store, "OLD_KEY", PASS) is None


def test_rename_missing_source(store):
    r = rename_variable(store, "MISSING", "NEW_KEY", PASS)
    assert not r.success
    assert "not found" in r.reason


def test_rename_destination_exists_no_overwrite(store):
    set_variable(store, "OLD_KEY", "v1", PASS)
    set_variable(store, "NEW_KEY", "v2", PASS)
    r = rename_variable(store, "OLD_KEY", "NEW_KEY", PASS)
    assert not r.success
    assert "exists" in r.reason
    assert get_variable(store, "OLD_KEY", PASS) == "v1"


def test_rename_destination_exists_with_overwrite(store):
    set_variable(store, "OLD_KEY", "v1", PASS)
    set_variable(store, "NEW_KEY", "v2", PASS)
    r = rename_variable(store, "OLD_KEY", "NEW_KEY", PASS, overwrite=True)
    assert r.success
    assert get_variable(store, "NEW_KEY", PASS) == "v1"


def test_rename_in_profile(store):
    set_profile_variable(store, "prod", "OLD", "val", PASS)
    r = rename_variable(store, "OLD", "NEW", PASS, profile="prod")
    assert r.success
    assert get_profile_variable(store, "prod", "NEW", PASS) == "val"
    assert get_profile_variable(store, "prod", "OLD", PASS) is None


def test_rename_all_profiles(store):
    for p in ["dev", "staging"]:
        set_profile_variable(store, p, "OLD", "value", PASS)
    results = rename_all_profiles(store, "OLD", "NEW", PASS, ["dev", "staging"])
    assert all(r.success for r in results)
    for p in ["dev", "staging"]:
        assert get_profile_variable(store, p, "NEW", PASS) == "value"


def test_rename_all_profiles_partial_miss(store):
    set_profile_variable(store, "dev", "OLD", "value", PASS)
    results = rename_all_profiles(store, "OLD", "NEW", PASS, ["dev", "staging"])
    assert results[0].success
    assert not results[1].success
