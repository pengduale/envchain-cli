import pytest
from pathlib import Path
from envchain.env_sync import sync_profiles, sync_profile_to_default, SyncResult
from envchain.profile import set_profile_variable, get_profile_variable, list_profile_keys
from envchain.store import get_variable

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_sync_profiles_copies_keys(store):
    set_profile_variable(store, "dev", "API_KEY", "abc", PASS)
    set_profile_variable(store, "dev", "DB_URL", "postgres://", PASS)
    result = sync_profiles(store, "dev", "staging", PASS)
    assert "API_KEY" in result.copied
    assert "DB_URL" in result.copied
    assert get_profile_variable(store, "staging", "API_KEY", PASS) == "abc"
    assert get_profile_variable(store, "staging", "DB_URL", PASS) == "postgres://"


def test_sync_profiles_skips_existing_without_overwrite(store):
    set_profile_variable(store, "dev", "API_KEY", "new", PASS)
    set_profile_variable(store, "staging", "API_KEY", "old", PASS)
    result = sync_profiles(store, "dev", "staging", PASS, overwrite=False)
    assert "API_KEY" in result.skipped
    assert get_profile_variable(store, "staging", "API_KEY", PASS) == "old"


def test_sync_profiles_overwrites_when_flag_set(store):
    set_profile_variable(store, "dev", "API_KEY", "new", PASS)
    set_profile_variable(store, "staging", "API_KEY", "old", PASS)
    result = sync_profiles(store, "dev", "staging", PASS, overwrite=True)
    assert "API_KEY" in result.overwritten
    assert get_profile_variable(store, "staging", "API_KEY", PASS) == "new"


def test_sync_profile_to_default_copies(store):
    set_profile_variable(store, "dev", "TOKEN", "tok123", PASS)
    result = sync_profile_to_default(store, "dev", PASS)
    assert "TOKEN" in result.copied
    assert get_variable(store, "TOKEN", PASS) == "tok123"


def test_sync_profile_to_default_skips_existing(store):
    from envchain.store import set_variable
    set_variable(store, "TOKEN", "existing", PASS)
    set_profile_variable(store, "dev", "TOKEN", "new", PASS)
    result = sync_profile_to_default(store, "dev", PASS, overwrite=False)
    assert "TOKEN" in result.skipped
    assert get_variable(store, "TOKEN", PASS) == "existing"


def test_sync_empty_profile_returns_empty_result(store):
    result = sync_profiles(store, "empty", "dst", PASS)
    assert result.copied == []
    assert result.skipped == []
    assert result.overwritten == []
