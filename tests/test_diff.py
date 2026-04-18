"""Tests for envchain.diff module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envchain.crypto import encrypt
from envchain.diff import diff_snapshots, diff_snapshot_vs_live, _compute_diff, DiffEntry


PASS = "testpass"


def _make_snapshot(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps({k: encrypt(v, PASS) for k, v in data.items()}))
    return p


def test_compute_diff_added():
    entries = _compute_diff({}, {"FOO": "bar"})
    assert any(e.key == "FOO" and e.status == "added" for e in entries)


def test_compute_diff_removed():
    entries = _compute_diff({"FOO": "bar"}, {})
    assert any(e.key == "FOO" and e.status == "removed" for e in entries)


def test_compute_diff_changed():
    entries = _compute_diff({"FOO": "old"}, {"FOO": "new"})
    assert any(e.key == "FOO" and e.status == "changed" and e.old_value == "old" and e.new_value == "new" for e in entries)


def test_compute_diff_unchanged():
    entries = _compute_diff({"FOO": "same"}, {"FOO": "same"})
    assert any(e.key == "FOO" and e.status == "unchanged" for e in entries)


def test_diff_snapshots_added(tmp_path):
    snap_a = _make_snapshot(tmp_path, "a.json", {"KEY1": "val1"})
    snap_b = _make_snapshot(tmp_path, "b.json", {"KEY1": "val1", "KEY2": "val2"})
    entries = diff_snapshots(snap_a, snap_b, PASS)
    statuses = {e.key: e.status for e in entries}
    assert statuses["KEY1"] == "unchanged"
    assert statuses["KEY2"] == "added"


def test_diff_snapshots_changed(tmp_path):
    snap_a = _make_snapshot(tmp_path, "a.json", {"KEY1": "old"})
    snap_b = _make_snapshot(tmp_path, "b.json", {"KEY1": "new"})
    entries = diff_snapshots(snap_a, snap_b, PASS)
    assert entries[0].status == "changed"
    assert entries[0].old_value == "old"
    assert entries[0].new_value == "new"


def test_diff_snapshot_vs_live(tmp_path):
    from envchain.store import set_variable
    store = tmp_path / "live.json"
    set_variable(store, "LIVE_KEY", "live_val", PASS)
    snap = _make_snapshot(tmp_path, "snap.json", {"LIVE_KEY": "old_val"})
    entries = diff_snapshot_vs_live(snap, store, PASS)
    statuses = {e.key: e.status for e in entries}
    assert statuses["LIVE_KEY"] == "changed"


def test_diff_empty_snapshots(tmp_path):
    snap_a = _make_snapshot(tmp_path, "a.json", {})
    snap_b = _make_snapshot(tmp_path, "b.json", {})
    entries = diff_snapshots(snap_a, snap_b, PASS)
    assert entries == []
