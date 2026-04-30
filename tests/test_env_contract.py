"""Tests for envchain.env_contract."""

import pytest
from pathlib import Path
from envchain.env_contract import (
    set_contract,
    get_contract,
    remove_contract,
    enforce_contract,
    list_contracts,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "envchain.json")


def test_set_and_get_contract(store):
    result = set_contract(store, "API_KEY", value_type="string", min_length=8)
    assert result.ok
    contract = get_contract(store, "API_KEY")
    assert contract is not None
    assert contract["type"] == "string"
    assert contract["min_length"] == 8


def test_get_missing_contract_returns_none(store):
    assert get_contract(store, "MISSING") is None


def test_invalid_type_returns_error(store):
    result = set_contract(store, "KEY", value_type="uuid")
    assert not result.ok
    assert "Invalid type" in result.message


def test_remove_contract_returns_true(store):
    set_contract(store, "MY_KEY")
    assert remove_contract(store, "MY_KEY") is True
    assert get_contract(store, "MY_KEY") is None


def test_remove_missing_contract_returns_false(store):
    assert remove_contract(store, "GHOST") is False


def test_enforce_string_min_length_pass(store):
    set_contract(store, "TOKEN", min_length=4)
    result = enforce_contract(store, "TOKEN", "abcdef")
    assert result.ok


def test_enforce_string_min_length_fail(store):
    set_contract(store, "TOKEN", min_length=10)
    result = enforce_contract(store, "TOKEN", "short")
    assert not result.ok
    assert "too short" in result.message


def test_enforce_max_length_fail(store):
    set_contract(store, "CODE", max_length=4)
    result = enforce_contract(store, "CODE", "toolongvalue")
    assert not result.ok
    assert "too long" in result.message


def test_enforce_integer_type_pass(store):
    set_contract(store, "PORT", value_type="integer")
    result = enforce_contract(store, "PORT", "8080")
    assert result.ok


def test_enforce_integer_type_fail(store):
    set_contract(store, "PORT", value_type="integer")
    result = enforce_contract(store, "PORT", "not-a-number")
    assert not result.ok
    assert "integer" in result.message


def test_enforce_boolean_type_pass(store):
    set_contract(store, "FLAG", value_type="boolean")
    for val in ("true", "false", "1", "0", "yes", "no"):
        assert enforce_contract(store, "FLAG", val).ok


def test_enforce_boolean_type_fail(store):
    set_contract(store, "FLAG", value_type="boolean")
    result = enforce_contract(store, "FLAG", "maybe")
    assert not result.ok


def test_enforce_pattern_pass(store):
    set_contract(store, "ENV", pattern=r"(dev|staging|prod)")
    assert enforce_contract(store, "ENV", "prod").ok


def test_enforce_pattern_fail(store):
    set_contract(store, "ENV", pattern=r"(dev|staging|prod)")
    result = enforce_contract(store, "ENV", "local")
    assert not result.ok
    assert "pattern" in result.message


def test_enforce_required_empty_fails(store):
    set_contract(store, "SECRET", required=True)
    result = enforce_contract(store, "SECRET", "")
    assert not result.ok
    assert "required" in result.message


def test_enforce_no_contract_always_passes(store):
    result = enforce_contract(store, "UNDEFINED_KEY", "anything")
    assert result.ok
    assert "No contract" in result.message


def test_list_contracts_empty(store):
    assert list_contracts(store) == {}


def test_list_contracts_multiple(store):
    set_contract(store, "A", value_type="string")
    set_contract(store, "B", value_type="integer")
    contracts = list_contracts(store)
    assert set(contracts.keys()) == {"A", "B"}
