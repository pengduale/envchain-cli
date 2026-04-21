"""Tests for envchain.env_secret_strength."""
from __future__ import annotations

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.env_secret_strength import (
    _entropy,
    _score_value,
    _level,
    check_strength,
    check_all_strength,
    StrengthResult,
)

PASS = "test-passphrase"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "store.json"


# --- unit tests for helpers ---

def test_entropy_empty_string():
    assert _entropy("") == 0.0


def test_entropy_single_char():
    assert _entropy("aaaa") == 0.0


def test_entropy_high_variety():
    val = "aAbBcC123!@#"
    assert _entropy(val) > 3.0


def test_score_weak_short_value():
    score, tips = _score_value("abc")
    assert score < 25
    assert any("16 characters" in t for t in tips)


def test_score_strong_complex_value():
    strong = "Tr0ub4dor&3-XyZ!2025$secret"
    score, tips = _score_value(strong)
    assert score >= 75


def test_score_missing_uppercase_gives_tip():
    _, tips = _score_value("alllowercase123!")
    assert any("uppercase" in t for t in tips)


def test_score_missing_special_gives_tip():
    _, tips = _score_value("NoSpecialChars123")
    assert any("special" in t for t in tips)


def test_level_thresholds():
    assert _level(10) == "weak"
    assert _level(25) == "fair"
    assert _level(50) == "good"
    assert _level(75) == "strong"
    assert _level(100) == "strong"


# --- integration tests ---

def test_check_strength_returns_result(store: Path):
    set_variable(store, PASS, "MY_TOKEN", "Tr0ub4dor&3-XyZ!2025$")
    result = check_strength(store, PASS, "MY_TOKEN")
    assert isinstance(result, StrengthResult)
    assert result.key == "MY_TOKEN"
    assert result.score > 0
    assert result.level in ("weak", "fair", "good", "strong")


def test_check_strength_weak_value(store: Path):
    set_variable(store, PASS, "WEAK_KEY", "abc")
    result = check_strength(store, PASS, "WEAK_KEY")
    assert result.level == "weak"
    assert len(result.suggestions) > 0


def test_check_strength_missing_key_raises(store: Path):
    with pytest.raises(KeyError, match="MISSING"):
        check_strength(store, PASS, "MISSING")


def test_check_all_strength_empty_store(store: Path):
    results = check_all_strength(store, PASS)
    assert results == []


def test_check_all_strength_multiple_keys(store: Path):
    set_variable(store, PASS, "KEY_A", "short")
    set_variable(store, PASS, "KEY_B", "Tr0ub4dor&3-XyZ!2025$secret")
    results = check_all_strength(store, PASS)
    assert len(results) == 2
    keys = {r.key for r in results}
    assert keys == {"KEY_A", "KEY_B"}


def test_repr_contains_key_and_level(store: Path):
    set_variable(store, PASS, "REPR_KEY", "SomeValue123!")
    result = check_strength(store, PASS, "REPR_KEY")
    assert "REPR_KEY" in repr(result)
    assert result.level in repr(result)
