import os
import pytest
from unittest.mock import patch
from envchain.env_diff_check import diff_live_vs_stored, summary, EnvDiffEntry
from envchain.store import set_variable


@pytest.fixture
def store(tmp_path):
    path = str(tmp_path / "store.json")
    set_variable(path, "MATCH_KEY", "same_value", "pass")
    set_variable(path, "DIFF_KEY", "stored_value", "pass")
    set_variable(path, "STORED_ONLY", "only_here", "pass")
    return path


def test_match_status(store):
    with patch.dict(os.environ, {"MATCH_KEY": "same_value"}, clear=False):
        entries = diff_live_vs_stored(store, "pass", keys=["MATCH_KEY"])
    assert len(entries) == 1
    assert entries[0].status == "match"


def test_mismatch_status(store):
    with patch.dict(os.environ, {"DIFF_KEY": "live_value"}, clear=False):
        entries = diff_live_vs_stored(store, "pass", keys=["DIFF_KEY"])
    assert entries[0].status == "mismatch"
    assert entries[0].stored == "stored_value"
    assert entries[0].live == "live_value"


def test_stored_only_status(store):
    env_without_key = {k: v for k, v in os.environ.items() if k != "STORED_ONLY"}
    with patch.dict(os.environ, env_without_key, clear=True):
        entries = diff_live_vs_stored(store, "pass", keys=["STORED_ONLY"])
    assert entries[0].status == "stored_only"
    assert entries[0].live is None


def test_live_only_included(store):
    with patch.dict(os.environ, {"LIVE_ONLY_VAR": "hello"}, clear=False):
        entries = diff_live_vs_stored(store, "pass", include_live_only=True)
    keys = [e.key for e in entries]
    assert "LIVE_ONLY_VAR" in keys
    live_entry = next(e for e in entries if e.key == "LIVE_ONLY_VAR")
    assert live_entry.status == "live_only"
    assert live_entry.stored is None


def test_live_only_excluded_by_default(store):
    with patch.dict(os.environ, {"LIVE_ONLY_VAR": "hello"}, clear=False):
        entries = diff_live_vs_stored(store, "pass")
    keys = [e.key for e in entries]
    assert "LIVE_ONLY_VAR" not in keys


def test_summary_counts(store):
    entries = [
        EnvDiffEntry("A", "x", "x"),
        EnvDiffEntry("B", "x", "y"),
        EnvDiffEntry("C", "x", None),
        EnvDiffEntry("D", None, "z"),
    ]
    counts = summary(entries)
    assert counts["match"] == 1
    assert counts["mismatch"] == 1
    assert counts["stored_only"] == 1
    assert counts["live_only"] == 1


def test_repr_entry():
    e = EnvDiffEntry("FOO", "a", "b")
    assert "mismatch" in repr(e)
