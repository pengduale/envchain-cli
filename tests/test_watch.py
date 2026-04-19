"""Tests for envchain.watch."""
from __future__ import annotations
import pytest
import time
from pathlib import Path
from envchain.store import set_variable, list_keys
from envchain.watch import watch_store, diff_on_change

PASS = "watchpass"


@pytest.fixture()
def store(tmp_path):
    p = tmp_path / "store.json"
    set_variable(p, "ALPHA", "one", PASS)
    return p


def test_watch_calls_callback_on_change(store, tmp_path):
    calls = []

    def cb(path):
        calls.append(path)

    # Touch the file after a tiny sleep to simulate change
    import threading

    def _touch():
        time.sleep(0.05)
        store.write_bytes(store.read_bytes())  # same content, new mtime

    t = threading.Thread(target=_touch)
    t.start()
    watch_store(store, cb, interval=0.02, max_iterations=10)
    t.join()
    assert len(calls) >= 1


def test_watch_no_callback_if_unchanged(store):
    calls = []
    watch_store(store, lambda p: calls.append(p), interval=0.01, max_iterations=5)
    assert calls == []


def test_diff_on_change_detects_added(store):
    cb = diff_on_change(store, PASS)
    set_variable(store, "BETA", "two", PASS)
    output = []
    import io, sys
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        cb(store)
    assert "BETA" in buf.getvalue()
    assert "+" in buf.getvalue()


def test_diff_on_change_detects_changed(store):
    cb = diff_on_change(store, PASS)
    set_variable(store, "ALPHA", "updated", PASS)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        cb(store)
    assert "ALPHA" in buf.getvalue()
    assert "~" in buf.getvalue()


def test_diff_on_change_no_output_when_same(store, capsys):
    cb = diff_on_change(store, PASS)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        cb(store)
    assert buf.getvalue() == ""
