import pytest
from pathlib import Path
from envchain.store import set_variable
from envchain.env_check import CheckRule, check_variable, check_all, check_keys_exist

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    p = str(tmp_path / "store.json")
    set_variable(p, "API_KEY", "supersecret123", PASS)
    set_variable(p, "SHORT", "ab", PASS)
    set_variable(p, "NUMERIC", "12345", PASS)
    return p


def test_check_present_and_valid(store):
    result = check_variable(store, PASS, CheckRule(key="API_KEY"))
    assert result.present
    assert result.valid


def test_check_missing_required(store):
    result = check_variable(store, PASS, CheckRule(key="MISSING"))
    assert not result.present
    assert not result.valid
    assert "missing" in result.message


def test_check_missing_optional(store):
    result = check_variable(store, PASS, CheckRule(key="MISSING", required=False))
    assert not result.present
    assert result.valid
    assert "optional" in result.message


def test_check_min_length_pass(store):
    result = check_variable(store, PASS, CheckRule(key="API_KEY", min_length=5))
    assert result.valid


def test_check_min_length_fail(store):
    result = check_variable(store, PASS, CheckRule(key="SHORT", min_length=5))
    assert result.present
    assert not result.valid
    assert "minimum length" in result.message


def test_check_pattern_match(store):
    result = check_variable(store, PASS, CheckRule(key="NUMERIC", pattern=r"\d+"))
    assert result.valid


def test_check_pattern_no_match(store):
    result = check_variable(store, PASS, CheckRule(key="API_KEY", pattern=r"\d+"))
    assert not result.valid
    assert "pattern" in result.message


def test_check_all_returns_all(store):
    rules = [CheckRule("API_KEY"), CheckRule("MISSING", required=False), CheckRule("GONE")]
    results = check_all(store, PASS, rules)
    assert len(results) == 3


def test_check_keys_exist(store):
    results = check_keys_exist(store, PASS, ["API_KEY", "NOPE"])
    assert results[0].valid
    assert not results[1].valid
