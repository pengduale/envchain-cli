"""Tests for envchain.env_staleness."""

from __future__ import annotations

import time
import pytest
from pathlib import Path

from envchain.env_staleness import (
    touch_key,
    set_threshold,
    check_staleness,
    list_stale,
    _staleness_path,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_touch_key_creates_record(store):
    result = touch_key(store, "MY_KEY")
    assert result.key == "MY_KEY"
    assert result.is_stale is False
    assert result.age_days == 0.0


def test_touch_key_persists(store):
    touch_key(store, "MY_KEY")
    result = check_staleness(store, "MY_KEY")
    assert result is not None
    assert result.key == "MY_KEY"
    assert result.age_days < 1.0


def test_check_staleness_missing_key_returns_none(store):
    result = check_staleness(store, "MISSING")
    assert result is None


def test_set_threshold_updates_value(store):
    touch_key(store, "API_KEY")
    result = set_threshold(store, "API_KEY", 14)
    assert result.threshold_days == 14
    assert result.key == "API_KEY"


def test_set_threshold_invalid_raises(store):
    with pytest.raises(ValueError, match="positive"):
        set_threshold(store, "API_KEY", 0)


def test_set_threshold_negative_raises(store):
    with pytest.raises(ValueError):
        set_threshold(store, "API_KEY", -5)


def test_key_is_fresh_when_just_touched(store):
    touch_key(store, "DB_PASS")
    set_threshold(store, "DB_PASS", 7)
    result = check_staleness(store, "DB_PASS")
    assert result is not None
    assert result.is_stale is False


def test_key_is_stale_when_threshold_exceeded(store):
    data_path = _staleness_path(store)
    import json
    old_time = time.time() - (10 * 86400)  # 10 days ago
    data_path.write_text(json.dumps({
        "OLD_KEY": {"last_updated": old_time, "threshold_days": 5}
    }))
    result = check_staleness(store, "OLD_KEY")
    assert result is not None
    assert result.is_stale is True
    assert result.age_days > 9.0


def test_list_stale_returns_only_stale_keys(store):
    import json
    now = time.time()
    data_path = _staleness_path(store)
    data_path.write_text(json.dumps({
        "FRESH_KEY": {"last_updated": now, "threshold_days": 30},
        "STALE_KEY": {"last_updated": now - 20 * 86400, "threshold_days": 10},
    }))
    stale = list_stale(store)
    keys = [r.key for r in stale]
    assert "STALE_KEY" in keys
    assert "FRESH_KEY" not in keys


def test_list_stale_empty_store_returns_empty(store):
    result = list_stale(store)
    assert result == []


def test_repr_contains_key_and_status(store):
    import json
    data_path = _staleness_path(store)
    old_time = time.time() - 20 * 86400
    data_path.write_text(json.dumps({
        "X": {"last_updated": old_time, "threshold_days": 5}
    }))
    result = check_staleness(store, "X")
    assert "STALE" in repr(result)
    assert "X" in repr(result)
