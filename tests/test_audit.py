"""Tests for envchain.audit module."""

import pytest
from pathlib import Path
from envchain.audit import log_event, read_events, clear_log


@pytest.fixture
def store_dir(tmp_path):
    return str(tmp_path)


def test_log_creates_file(store_dir):
    log_event(store_dir, "set", "MY_VAR")
    assert (Path(store_dir) / ".envchain_audit.jsonl").exists()


def test_read_events_empty(store_dir):
    assert read_events(store_dir) == []


def test_log_and_read_single(store_dir):
    log_event(store_dir, "set", "FOO")
    events = read_events(store_dir)
    assert len(events) == 1
    assert events[0]["action"] == "set"
    assert events[0]["key"] == "FOO"
    assert "timestamp" in events[0]


def test_log_multiple_events(store_dir):
    log_event(store_dir, "set", "A")
    log_event(store_dir, "get", "A")
    log_event(store_dir, "delete", "A")
    events = read_events(store_dir)
    assert len(events) == 3
    assert [e["action"] for e in events] == ["set", "get", "delete"]


def test_log_extra_fields(store_dir):
    log_event(store_dir, "rotate", "*", {"count": 3})
    events = read_events(store_dir)
    assert events[0]["count"] == 3


def test_clear_log(store_dir):
    log_event(store_dir, "set", "X")
    clear_log(store_dir)
    assert read_events(store_dir) == []
    assert not (Path(store_dir) / ".envchain_audit.jsonl").exists()


def test_clear_log_no_file(store_dir):
    # Should not raise if file doesn't exist
    clear_log(store_dir)
