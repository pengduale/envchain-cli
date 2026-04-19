import pytest
import os
from envchain.store import set_variable
from envchain.env_validate import (
    ValidationRule, validate_variable, validate_all, load_schema
)

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    p = str(tmp_path / "store.json")
    set_variable(p, PASS, "API_KEY", "supersecret")
    set_variable(p, PASS, "ENV", "production")
    set_variable(p, PASS, "PORT", "8080")
    return p


def test_validate_present_key_passes(store):
    rule = ValidationRule(key="API_KEY")
    r = validate_variable(store, PASS, rule)
    assert r.passed
    assert r.message == "ok"


def test_validate_missing_required_fails(store):
    rule = ValidationRule(key="MISSING_KEY", required=True)
    r = validate_variable(store, PASS, rule)
    assert not r.passed
    assert "missing" in r.message


def test_validate_missing_optional_passes(store):
    rule = ValidationRule(key="MISSING_KEY", required=False)
    r = validate_variable(store, PASS, rule)
    assert r.passed


def test_validate_pattern_match(store):
    rule = ValidationRule(key="PORT", pattern=r"\d+")
    r = validate_variable(store, PASS, rule)
    assert r.passed


def test_validate_pattern_no_match(store):
    rule = ValidationRule(key="ENV", pattern=r"\d+")
    r = validate_variable(store, PASS, rule)
    assert not r.passed
    assert "pattern" in r.message


def test_validate_min_length_pass(store):
    rule = ValidationRule(key="API_KEY", min_length=5)
    r = validate_variable(store, PASS, rule)
    assert r.passed


def test_validate_min_length_fail(store):
    rule = ValidationRule(key="ENV", min_length=100)
    r = validate_variable(store, PASS, rule)
    assert not r.passed
    assert "short" in r.message


def test_validate_allowed_values_pass(store):
    rule = ValidationRule(key="ENV", allowed_values=["production", "staging"])
    r = validate_variable(store, PASS, rule)
    assert r.passed


def test_validate_allowed_values_fail(store):
    rule = ValidationRule(key="ENV", allowed_values=["dev", "test"])
    r = validate_variable(store, PASS, rule)
    assert not r.passed


def test_validate_all_returns_all_results(store):
    rules = [
        ValidationRule(key="API_KEY"),
        ValidationRule(key="ENV"),
        ValidationRule(key="NOPE", required=False),
    ]
    results = validate_all(store, PASS, rules)
    assert len(results) == 3
    assert all(r.passed for r in results)


def test_load_schema_builds_rules():
    schema = {
        "API_KEY": {"required": True, "min_length": 8},
        "DEBUG": {"required": False, "allowed_values": ["true", "false"]},
    }
    rules = load_schema(schema)
    assert len(rules) == 2
    keys = {r.key for r in rules}
    assert "API_KEY" in keys and "DEBUG" in keys
