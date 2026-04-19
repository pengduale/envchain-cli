import pytest
from pathlib import Path
from envchain.env_squash import squash_profiles
from envchain.profile import set_profile_variable, get_profile_variable

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return tmp_path


def _set(store, profile, key, value):
    set_profile_variable(store, PASS, profile, key, value)


def _get(store, profile, key):
    return get_profile_variable(store, PASS, profile, key)


def test_squash_basic(store):
    _set(store, "dev", "KEY1", "v1")
    _set(store, "staging", "KEY2", "v2")
    results = squash_profiles(store, PASS, ["dev", "staging"], dest="merged")
    written = [r for r in results if r.written]
    assert len(written) == 2
    assert _get(store, "merged", "KEY1") == "v1"
    assert _get(store, "merged", "KEY2") == "v2"


def test_squash_skips_existing_without_overwrite(store):
    _set(store, "dev", "KEY1", "original")
    _set(store, "merged", "KEY1", "existing")
    results = squash_profiles(store, PASS, ["dev"], dest="merged", overwrite=False)
    skipped = [r for r in results if not r.written]
    assert any(r.key == "KEY1" for r in skipped)
    assert _get(store, "merged", "KEY1") == "existing"


def test_squash_overwrites_when_flag_set(store):
    _set(store, "dev", "KEY1", "new_value")
    _set(store, "merged", "KEY1", "old_value")
    results = squash_profiles(store, PASS, ["dev"], dest="merged", overwrite=True)
    written = [r for r in results if r.written]
    assert any(r.key == "KEY1" for r in written)
    assert _get(store, "merged", "KEY1") == "new_value"


def test_squash_first_profile_wins_without_overwrite(store):
    _set(store, "dev", "SHARED", "from_dev")
    _set(store, "staging", "SHARED", "from_staging")
    results = squash_profiles(store, PASS, ["dev", "staging"], dest="out", overwrite=False)
    assert _get(store, "out", "SHARED") == "from_dev"
    skipped = [r for r in results if not r.written and r.key == "SHARED"]
    assert skipped


def test_squash_missing_profile_skipped(store):
    _set(store, "dev", "KEY1", "v1")
    results = squash_profiles(store, PASS, ["dev", "nonexistent"], dest="out")
    written = [r for r in results if r.written]
    assert len(written) == 1
    assert written[0].key == "KEY1"
