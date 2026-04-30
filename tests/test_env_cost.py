"""Tests for envchain.env_cost module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_cost import set_cost, get_cost, remove_cost, list_costs


@pytest.fixture
def store(tmp_path):
    return tmp_path / "store.json"


def test_set_and_get_cost(store):
    result = set_cost(store, "OPENAI_KEY", 0.02, "USD", note="per 1k tokens")
    assert result.ok
    assert result.key == "OPENAI_KEY"
    assert result.amount == 0.02
    assert result.currency == "USD"
    assert result.note == "per 1k tokens"


def test_get_cost_after_set(store):
    set_cost(store, "STRIPE_KEY", 0.30, "EUR")
    r = get_cost(store, "STRIPE_KEY")
    assert r is not None
    assert r.amount == 0.30
    assert r.currency == "EUR"
    assert r.note is None


def test_get_missing_cost_returns_none(store):
    result = get_cost(store, "MISSING_KEY")
    assert result is None


def test_invalid_currency_returns_error(store):
    result = set_cost(store, "MY_KEY", 1.0, "XYZ")
    assert not result.ok
    assert "Invalid currency" in result.error


def test_negative_amount_returns_error(store):
    result = set_cost(store, "MY_KEY", -5.0, "USD")
    assert not result.ok
    assert "non-negative" in result.error


def test_zero_amount_is_valid(store):
    result = set_cost(store, "FREE_KEY", 0.0, "USD")
    assert result.ok
    assert result.amount == 0.0


def test_overwrite_cost(store):
    set_cost(store, "KEY", 1.0, "USD")
    set_cost(store, "KEY", 2.5, "EUR", note="updated")
    r = get_cost(store, "KEY")
    assert r.amount == 2.5
    assert r.currency == "EUR"
    assert r.note == "updated"


def test_remove_cost_returns_true(store):
    set_cost(store, "KEY", 1.0, "USD")
    assert remove_cost(store, "KEY") is True
    assert get_cost(store, "KEY") is None


def test_remove_missing_cost_returns_false(store):
    assert remove_cost(store, "MISSING") is False


def test_list_costs_empty(store):
    assert list_costs(store) == []


def test_list_costs_multiple(store):
    set_cost(store, "KEY_A", 1.0, "USD")
    set_cost(store, "KEY_B", 2.0, "EUR")
    results = list_costs(store)
    keys = {r.key for r in results}
    assert keys == {"KEY_A", "KEY_B"}


def test_repr_ok(store):
    set_cost(store, "KEY", 0.5, "GBP")
    r = get_cost(store, "KEY")
    assert "KEY" in repr(r)
    assert "GBP" in repr(r)


def test_repr_error():
    from envchain.env_cost import CostResult
    r = CostResult("K", 0, "USD", None, ok=False, error="bad")
    assert "error" in repr(r)
