"""Tests for envchain.env_entropy_audit."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.env_entropy_audit import (
    _shannon_entropy,
    _classify,
    audit_store,
    summary,
    WEAK_THRESHOLD,
    FAIR_THRESHOLD,
)

PASS = "test-passphrase"


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "store.json"


# --- unit tests for helpers ---

def test_entropy_empty_string():
    assert _shannon_entropy("") == 0.0


def test_entropy_single_repeated_char():
    # All same chars → 0 entropy
    assert _shannon_entropy("aaaaaaa") == pytest.approx(0.0)


def test_entropy_two_equal_chars():
    # "ab" repeated → 1 bit per char
    result = _shannon_entropy("abababab")
    assert result == pytest.approx(1.0, abs=0.01)


def test_entropy_high_variety():
    value = "aB3!xZ9@qL#mW2$"
    result = _shannon_entropy(value)
    assert result > FAIR_THRESHOLD


def test_classify_weak():
    assert _classify(0.0) == "weak"
    assert _classify(WEAK_THRESHOLD - 0.01) == "weak"


def test_classify_fair():
    assert _classify(WEAK_THRESHOLD) == "fair"
    assert _classify(FAIR_THRESHOLD - 0.01) == "fair"


def test_classify_strong():
    assert _classify(FAIR_THRESHOLD) == "strong"
    assert _classify(5.0) == "strong"


# --- integration tests ---

def test_audit_empty_store(store: Path):
    result = audit_store(store, PASS)
    assert result == []


def test_audit_weak_value(store: Path):
    set_variable(store, "SIMPLE_KEY", "aaaa", PASS)
    entries = audit_store(store, PASS)
    assert len(entries) == 1
    e = entries[0]
    assert e.key == "SIMPLE_KEY"
    assert e.level == "weak"
    assert e.note is not None
    assert "rotating" in e.note


def test_audit_strong_value(store: Path):
    strong = "xK9#mP2@qZ5!nL8$"
    set_variable(store, "STRONG_KEY", strong, PASS)
    entries = audit_store(store, PASS)
    assert len(entries) == 1
    assert entries[0].level == "strong"
    assert entries[0].note is None


def test_audit_multiple_keys(store: Path):
    set_variable(store, "WEAK_VAR", "aaaa", PASS)
    set_variable(store, "STRONG_VAR", "xK9#mP2@qZ5!nL8$", PASS)
    entries = audit_store(store, PASS)
    assert len(entries) == 2
    levels = {e.key: e.level for e in entries}
    assert levels["WEAK_VAR"] == "weak"
    assert levels["STRONG_VAR"] == "strong"


def test_summary_counts(store: Path):
    set_variable(store, "W1", "aaaa", PASS)
    set_variable(store, "W2", "bbbb", PASS)
    set_variable(store, "S1", "xK9#mP2@qZ5!nL8$", PASS)
    entries = audit_store(store, PASS)
    s = summary(entries)
    assert s["total"] == 3
    assert s["weak"] == 2
    assert s["strong"] == 1
    assert s["fair"] == 0


def test_audit_entries_sorted_by_key(store: Path):
    set_variable(store, "ZEBRA", "aaaa", PASS)
    set_variable(store, "ALPHA", "aaaa", PASS)
    entries = audit_store(store, PASS)
    keys = [e.key for e in entries]
    assert keys == sorted(keys)
