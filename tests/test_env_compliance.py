"""Tests for envchain.env_compliance."""

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.env_compliance import (
    check_key_naming,
    check_value_not_empty,
    check_value_min_length,
    run_compliance,
    compliance_summary,
)


@pytest.fixture
def store(tmp_path):
    store_path = tmp_path / ".envchain"
    store_path.mkdir()
    return store_path


PASS = "supersecret"


def test_check_key_naming_valid():
    result = check_key_naming("MY_VAR")
    assert result.passed is True
    assert result.rule == "key_naming"


def test_check_key_naming_lowercase_fails():
    result = check_key_naming("my_var")
    assert result.passed is False
    assert "UPPER_SNAKE_CASE" in result.message


def test_check_key_naming_starts_with_digit_fails():
    result = check_key_naming("1VAR")
    assert result.passed is False


def test_check_value_not_empty_passes(store):
    set_variable(store, "API_KEY", "abc123", PASS)
    result = check_value_not_empty("API_KEY", store, PASS)
    assert result.passed is True


def test_check_value_not_empty_fails_on_missing(store):
    result = check_value_not_empty("MISSING_KEY", store, PASS)
    assert result.passed is False
    assert "empty" in result.message


def test_check_value_min_length_passes(store):
    set_variable(store, "TOKEN", "longenoughvalue", PASS)
    result = check_value_min_length("TOKEN", store, PASS, min_length=8)
    assert result.passed is True


def test_check_value_min_length_fails(store):
    set_variable(store, "SHORT", "abc", PASS)
    result = check_value_min_length("SHORT", store, PASS, min_length=8)
    assert result.passed is False
    assert "shorter than 8" in result.message


def test_run_compliance_all_pass(store):
    set_variable(store, "DB_PASSWORD", "securepassword", PASS)
    results = run_compliance(store, PASS, min_length=6, keys=["DB_PASSWORD"])
    assert all(r.passed for r in results)


def test_run_compliance_naming_failure(store):
    set_variable(store, "db_password", "securepassword", PASS)
    results = run_compliance(store, PASS, keys=["db_password"])
    naming_results = [r for r in results if r.rule == "key_naming"]
    assert len(naming_results) == 1
    assert naming_results[0].passed is False


def test_run_compliance_all_keys(store):
    set_variable(store, "KEY_ONE", "value_one_long", PASS)
    set_variable(store, "KEY_TWO", "value_two_long", PASS)
    results = run_compliance(store, PASS)
    keys_seen = {r.key for r in results}
    assert "KEY_ONE" in keys_seen
    assert "KEY_TWO" in keys_seen


def test_compliance_summary(store):
    set_variable(store, "GOOD_KEY", "longvalue123", PASS)
    results = run_compliance(store, PASS, keys=["GOOD_KEY"])
    summary = compliance_summary(results)
    assert summary["total"] == 3
    assert summary["passed"] == 3
    assert summary["failed"] == 0


def test_compliance_summary_with_failures(store):
    set_variable(store, "bad_key", "x", PASS)
    results = run_compliance(store, PASS, min_length=8, keys=["bad_key"])
    summary = compliance_summary(results)
    assert summary["failed"] >= 2  # naming + min_length
