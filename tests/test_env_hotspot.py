"""Tests for envchain.env_hotspot."""

from __future__ import annotations

import pytest

from envchain.env_hotspot import (
    HotspotResult,
    get_count,
    record_access,
    reset_hotspots,
    top_keys,
)


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def test_record_access_returns_result(store):
    result = record_access(store, "API_KEY")
    assert isinstance(result, HotspotResult)
    assert result.ok is True
    assert result.key == "API_KEY"
    assert result.count == 1


def test_record_access_increments_count(store):
    record_access(store, "API_KEY")
    record_access(store, "API_KEY")
    result = record_access(store, "API_KEY")
    assert result.count == 3


def test_record_access_empty_key_returns_error(store):
    result = record_access(store, "")
    assert result.ok is False
    assert result.error is not None


def test_get_count_missing_key_returns_none(store):
    assert get_count(store, "MISSING") is None


def test_get_count_after_record(store):
    record_access(store, "DB_URL")
    record_access(store, "DB_URL")
    assert get_count(store, "DB_URL") == 2


def test_top_keys_empty_store(store):
    assert top_keys(store) == []


def test_top_keys_returns_sorted_descending(store):
    record_access(store, "LOW")
    for _ in range(5):
        record_access(store, "HIGH")
    for _ in range(3):
        record_access(store, "MID")

    results = top_keys(store)
    assert results[0].key == "HIGH"
    assert results[1].key == "MID"
    assert results[2].key == "LOW"


def test_top_keys_respects_limit(store):
    for key in ["A", "B", "C", "D", "E"]:
        record_access(store, key)
    results = top_keys(store, n=3)
    assert len(results) == 3


def test_reset_hotspots_clears_data(store):
    record_access(store, "KEY1")
    record_access(store, "KEY2")
    removed = reset_hotspots(store)
    assert removed == 2
    assert get_count(store, "KEY1") is None


def test_reset_hotspots_empty_store_returns_zero(store):
    assert reset_hotspots(store) == 0


def test_hotspot_result_repr_ok():
    r = HotspotResult(key="X", count=7)
    assert "X" in repr(r)
    assert "7" in repr(r)


def test_hotspot_result_repr_error():
    r = HotspotResult(key="", count=0, ok=False, error="Key must not be empty")
    assert "error" in repr(r).lower()
