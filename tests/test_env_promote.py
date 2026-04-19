import pytest
import tempfile
import os
from envchain.env_promote import promote_variable, promote_all
from envchain.profile import set_profile_variable, get_profile_variable

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_promote_variable_basic(store):
    set_profile_variable(store, "dev", "API_KEY", "abc123", PASS)
    result = promote_variable(store, "API_KEY", "dev", "prod", PASS)
    assert not result.skipped
    assert get_profile_variable(store, "prod", "API_KEY", PASS) == "abc123"


def test_promote_variable_skips_missing_source(store):
    result = promote_variable(store, "MISSING", "dev", "prod", PASS)
    assert result.skipped
    assert "not found" in result.reason


def test_promote_variable_skips_existing_without_overwrite(store):
    set_profile_variable(store, "dev", "DB_URL", "dev-db", PASS)
    set_profile_variable(store, "prod", "DB_URL", "prod-db", PASS)
    result = promote_variable(store, "DB_URL", "dev", "prod", PASS, overwrite=False)
    assert result.skipped
    assert get_profile_variable(store, "prod", "DB_URL", PASS) == "prod-db"


def test_promote_variable_overwrites_when_flag_set(store):
    set_profile_variable(store, "dev", "DB_URL", "dev-db", PASS)
    set_profile_variable(store, "prod", "DB_URL", "prod-db", PASS)
    result = promote_variable(store, "DB_URL", "dev", "prod", PASS, overwrite=True)
    assert not result.skipped
    assert get_profile_variable(store, "prod", "DB_URL", PASS) == "dev-db"


def test_promote_all_copies_all_keys(store):
    set_profile_variable(store, "dev", "A", "1", PASS)
    set_profile_variable(store, "dev", "B", "2", PASS)
    results = promote_all(store, "dev", "prod", PASS)
    assert len(results) == 2
    assert all(not r.skipped for r in results)


def test_promote_all_with_key_filter(store):
    set_profile_variable(store, "dev", "A", "1", PASS)
    set_profile_variable(store, "dev", "B", "2", PASS)
    results = promote_all(store, "dev", "prod", PASS, keys=["A"])
    assert len(results) == 1
    assert results[0].key == "A"
    assert get_profile_variable(store, "prod", "B", PASS) is None


def test_promote_all_empty_source(store):
    results = promote_all(store, "empty", "prod", PASS)
    assert results == []
