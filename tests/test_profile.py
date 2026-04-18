"""Tests for profile module."""
import pytest
from pathlib import Path

from envchain.profile import (
    list_profiles,
    set_profile_variable,
    get_profile_variable,
    delete_profile_variable,
    list_profile_keys,
    DEFAULT_PROFILE,
)


PASS = "hunter2"


@pytest.fixture
def store(tmp_path):
    return tmp_path / "envchain.json"


def test_set_and_get_default_profile(store):
    set_profile_variable(store, DEFAULT_PROFILE, "KEY", "val", PASS)
    assert get_profile_variable(store, DEFAULT_PROFILE, "KEY", PASS) == "val"


def test_set_and_get_named_profile(store):
    set_profile_variable(store, "staging", "DB_URL", "postgres://staging", PASS)
    assert get_profile_variable(store, "staging", "DB_URL", PASS) == "postgres://staging"


def test_profiles_are_isolated(store):
    set_profile_variable(store, DEFAULT_PROFILE, "KEY", "default_val", PASS)
    set_profile_variable(store, "prod", "KEY", "prod_val", PASS)
    assert get_profile_variable(store, DEFAULT_PROFILE, "KEY", PASS) == "default_val"
    assert get_profile_variable(store, "prod", "KEY", PASS) == "prod_val"


def test_list_profiles_includes_default(store):
    set_profile_variable(store, DEFAULT_PROFILE, "A", "1", PASS)
    set_profile_variable(store, "dev", "B", "2", PASS)
    profiles = list_profiles(store)
    assert DEFAULT_PROFILE in profiles
    assert "dev" in profiles


def test_list_profiles_empty(store):
    profiles = list_profiles(store)
    assert profiles == []


def test_list_profile_keys(store):
    set_profile_variable(store, "dev", "X", "1", PASS)
    set_profile_variable(store, "dev", "Y", "2", PASS)
    keys = list_profile_keys(store, "dev", PASS)
    assert set(keys) == {"X", "Y"}


def test_delete_profile_variable(store):
    set_profile_variable(store, "dev", "TEMP", "val", PASS)
    delete_profile_variable(store, "dev", "TEMP", PASS)
    keys = list_profile_keys(store, "dev", PASS)
    assert "TEMP" not in keys


def test_named_profile_uses_separate_file(store):
    set_profile_variable(store, "qa", "K", "v", PASS)
    expected = store.parent / f"{store.stem}.qa.json"
    assert expected.exists()
    assert not store.exists()
