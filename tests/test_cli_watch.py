"""Tests for envchain.cli_watch."""
from __future__ import annotations
import pytest
from click.testing import CliRunner
import click
from pathlib import Path
from envchain.store import set_variable
from envchain.cli_watch import register_watch_commands

PASS = "testpass"


@pytest.fixture()
def store_path(tmp_path):
    p = tmp_path / "store.json"
    set_variable(p, "KEY", "val", PASS)
    return p


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def cli(store_path):
    @click.group()
    def root():
        pass

    def get_store(ctx):
        return store_path

    register_watch_commands(root, get_store)
    return root


def test_watch_start_stops_on_keyboard_interrupt(runner, cli, store_path):
    """Simulate max_iterations=0 by monkeypatching watch_store."""
    import envchain.cli_watch as cw
    original = __import__("envchain.watch", fromlist=["watch_store"]).watch_store

    calls = []

    def fake_watch(path, cb, interval=1.0, max_iterations=None):
        calls.append(path)
        raise KeyboardInterrupt

    import envchain.watch as wmod
    wmod.watch_store = fake_watch

    result = runner.invoke(cli, ["watch", "start", "--passphrase", PASS])
    wmod.watch_store = original

    assert result.exit_code == 0
    assert "Stopped" in result.output
    assert len(calls) == 1


def test_watch_start_prints_watching(runner, cli, store_path):
    import envchain.watch as wmod
    original = wmod.watch_store
    wmod.watch_store = lambda *a, **kw: None
    result = runner.invoke(cli, ["watch", "start", "--passphrase", PASS])
    wmod.watch_store = original
    assert "Watching" in result.output
