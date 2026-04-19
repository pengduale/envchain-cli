"""Tests for envchain.env_copy."""
import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.profile import set_profile_variable, get_profile_variable
from envchain.env_copy import copy_profile_to_profile, copy_default_to_profile

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return tmp_path / ".envchain"


def test_copy_profile_to_profile_basic(store):
    set_profile_variable(store, "dev", "API_KEY", "abc", PASS)
    set_profile_variable(store, "dev", "DB_URL", "postgres://", PASS)
    result = copy_profile_to_profile(store, "dev", "staging", PASS)
    assert "API_KEY" in result.copied
    assert "DB_URL" in result.copied
    assert get_profile_variable(store, "staging", "API_KEY", PASS) == "abc"


def test_copy_profile_skips_existing_without_overwrite(store):
    set_profile_variable(store, "dev", "KEY", "original", PASS)
    set_profile_variable(store, "prod", "KEY", "existing", PASS)
    result = copy_profile_to_profile(store, "dev", "prod", PASS, overwrite=False)
    assert "KEY" in result.skipped
    assert get_profile_variable(store, "prod", "KEY", PASS) == "existing"


def test_copy_profile_overwrites_when_flag_set(store):
    set_profile_variable(store, "dev", "KEY", "new_value", PASS)
    set_profile_variable(store, "prod", "KEY", "old_value", PASS)
    result = copy_profile_to_profile(store, "dev", "prod", PASS, overwrite=True)
    assert "KEY" in result.overwritten
    assert get_profile_variable(store, "prod", "KEY", PASS) == "new_value"


def test_copy_profile_subset_of_keys(store):
    set_profile_variable(store, "dev", "A", "1", PASS)
    set_profile_variable(store, "dev", "B", "2", PASS)
    result = copy_profile_to_profile(store, "dev", "staging", PASS, keys=["A"])
    assert "A" in result.copied
    assert "B" not in result.copied
    assert get_profile_variable(store, "staging", "B", PASS) is None


def test_copy_default_to_profile(store):
    set_variable(store, "TOKEN", "secret", PASS)
    result = copy_default_to_profile(store, "ci", PASS)
    assert "TOKEN" in result.copied
    assert get_profile_variable(store, "ci", "TOKEN", PASS) == "secret"


def test_copy_default_to_profile_skip_existing(store):
    set_variable(store, "TOKEN", "new", PASS)
    set_profile_variable(store, "ci", "TOKEN", "old", PASS)
    result = copy_default_to_profile(store, "ci", PASS, overwrite=False)
    assert "TOKEN" in result.skipped
    assert get_profile_variable(store, "ci", "TOKEN", PASS) == "old"


def test_copy_result_repr(store):
    set_profile_variable(store, "dev", "X", "1", PASS)
    result = copy_profile_to_profile(store, "dev", "prod", PASS)
    assert "CopyResult" in repr(result)
