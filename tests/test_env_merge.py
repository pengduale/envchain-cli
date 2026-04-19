import pytest
import tempfile, os
from envchain.env_merge import merge_profiles, merge_summary
from envchain.profile import set_profile_variable, get_profile_variable

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def _set(store, profile, key, value):
    set_profile_variable(store, profile, key, value, PASS)


def _get(store, profile, key):
    return get_profile_variable(store, profile, key, PASS)


def test_merge_copies_keys(store):
    _set(store, "dev", "API_KEY", "dev-key")
    results = merge_profiles(store, ["dev"], "staging", PASS)
    assert any(r.key == "API_KEY" and r.status == "copied" for r in results)
    assert _get(store, "staging", "API_KEY") == "dev-key"


def test_merge_skips_existing_without_overwrite(store):
    _set(store, "dev", "API_KEY", "dev-key")
    _set(store, "staging", "API_KEY", "staging-key")
    results = merge_profiles(store, ["dev"], "staging", PASS, overwrite=False)
    assert any(r.key == "API_KEY" and r.status == "skipped" for r in results)
    assert _get(store, "staging", "API_KEY") == "staging-key"


def test_merge_overwrites_when_flag_set(store):
    _set(store, "dev", "API_KEY", "dev-key")
    _set(store, "staging", "API_KEY", "old")
    results = merge_profiles(store, ["dev"], "staging", PASS, overwrite=True)
    assert any(r.key == "API_KEY" and r.status == "overwritten" for r in results)
    assert _get(store, "staging", "API_KEY") == "dev-key"


def test_merge_multiple_sources_order(store):
    _set(store, "base", "KEY", "base-val")
    _set(store, "override", "KEY", "override-val")
    merge_profiles(store, ["base", "override"], "prod", PASS, overwrite=True)
    assert _get(store, "prod", "KEY") == "override-val"


def test_merge_key_filter(store):
    _set(store, "dev", "API_KEY", "k")
    _set(store, "dev", "SECRET", "s")
    results = merge_profiles(store, ["dev"], "staging", PASS, keys=["API_KEY"])
    keys = [r.key for r in results]
    assert "API_KEY" in keys
    assert "SECRET" not in keys


def test_merge_empty_source(store):
    results = merge_profiles(store, ["empty"], "target", PASS)
    assert results == []


def test_merge_summary_counts(store):
    _set(store, "dev", "A", "1")
    _set(store, "dev", "B", "2")
    _set(store, "staging", "B", "existing")
    results = merge_profiles(store, ["dev"], "staging", PASS, overwrite=False)
    s = merge_summary(results)
    assert s["copied"] == 1
    assert s["skipped"] == 1
    assert s["overwritten"] == 0


def test_merge_does_not_copy_to_source_profile(store):
    """Merging a profile into itself should skip all keys since they already exist."""
    _set(store, "dev", "API_KEY", "dev-key")
    _set(store, "dev", "SECRET", "dev-secret")
    results = merge_profiles(store, ["dev"], "dev", PASS, overwrite=False)
    assert all(r.status == "skipped" for r in results)
    assert _get(store, "dev", "API_KEY") == "dev-key"
    assert _get(store, "dev", "SECRET") == "dev-secret"
