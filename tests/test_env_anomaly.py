"""Tests for envchain.env_anomaly."""

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.env_anomaly import (
    AnomalyResult,
    _entropy,
    _check_value,
    scan_store,
    scan_key,
)

PASS = "test-pass"


@pytest.fixture
def store(tmp_path):
    return tmp_path / "store.json"


# --- unit tests for helpers ---

def test_entropy_empty_string():
    assert _entropy("") == 0.0


def test_entropy_single_char():
    assert _entropy("aaaa") == 0.0


def test_entropy_high_variety():
    val = "aAbBcCdDeEfFgG1234567890!@#$"
    assert _entropy(val) > 4.0


def test_check_value_empty_returns_anomaly():
    results = _check_value("MY_KEY", "")
    assert len(results) == 1
    assert results[0].anomaly_type == "empty_value"
    assert results[0].severity == "medium"


def test_check_value_normal_string_no_anomaly():
    results = _check_value("APP_ENV", "production")
    assert results == []


def test_check_value_high_entropy_flagged():
    # 40-char random-looking hex string
    val = "a3f1c9e2b7d04856f1a2c3d4e5f60718293a4b5c"
    results = _check_value("SECRET_TOKEN", val)
    types = {r.anomaly_type for r in results}
    assert "high_entropy" in types or "plaintext_secret_pattern" in types


def test_check_value_oversized_flagged():
    val = "x" * 5000
    results = _check_value("BIG_KEY", val)
    types = {r.anomaly_type for r in results}
    assert "oversized_value" in types


def test_check_value_plaintext_secret_pattern():
    results = _check_value("CONFIG", "password=supersecret")
    types = {r.anomaly_type for r in results}
    assert "plaintext_secret_pattern" in types


# --- integration tests with store ---

def test_scan_key_missing_returns_anomaly(store):
    results = scan_key(store, "NONEXISTENT", PASS)
    assert len(results) == 1
    assert results[0].anomaly_type == "missing_key"


def test_scan_key_clean_value_no_anomaly(store):
    set_variable(store, "APP_ENV", "staging", PASS)
    results = scan_key(store, "APP_ENV", PASS)
    assert results == []


def test_scan_store_empty_returns_empty(store):
    results = scan_store(store, PASS)
    assert results == []


def test_scan_store_detects_anomalies(store):
    set_variable(store, "CLEAN", "hello", PASS)
    set_variable(store, "SUSPICIOUS", "a3f1c9e2b7d04856f1a2c3d4e5f60718293a4b5c", PASS)
    results = scan_store(store, PASS)
    flagged_keys = {r.key for r in results}
    assert "SUSPICIOUS" in flagged_keys
    assert "CLEAN" not in flagged_keys


def test_anomaly_result_repr():
    r = AnomalyResult("MY_KEY", "high_entropy", "detail", "high")
    assert "MY_KEY" in repr(r)
    assert "high_entropy" in repr(r)
