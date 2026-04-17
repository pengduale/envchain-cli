"""Tests for CLI audit commands."""

import pytest
from click.testing import CliRunner
from envchain.cli import cli
from envchain.audit import log_event


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store_path(tmp_path):
    return str(tmp_path / "store.json")


def invoke(runner, store_path, args, passphrase="pass", input_str=None):
    env = {"ENVCHAIN_STORE": store_path, "ENVCHAIN_PASSPHRASE": passphrase}
    return runner.invoke(cli, args, env=env, input=input_str, catch_exceptions=False)


def test_audit_empty(runner, store_path, tmp_path):
    result = invoke(runner, store_path, ["audit"])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_audit_shows_events(runner, store_path, tmp_path):
    store_dir = str(tmp_path)
    log_event(store_dir, "set", "DB_URL")
    env = {"ENVCHAIN_STORE": str(tmp_path / "store.json"), "ENVCHAIN_PASSPHRASE": "pass"}
    result = runner.invoke(cli, ["audit"], env=env, catch_exceptions=False)
    assert "SET" in result.output
    assert "DB_URL" in result.output


def test_audit_filter_action(runner, store_path, tmp_path):
    store_dir = str(tmp_path)
    log_event(store_dir, "set", "A")
    log_event(store_dir, "get", "B")
    env = {"ENVCHAIN_STORE": str(tmp_path / "store.json"), "ENVCHAIN_PASSPHRASE": "pass"}
    result = runner.invoke(cli, ["audit", "--action", "get"], env=env, catch_exceptions=False)
    assert "GET" in result.output
    assert "SET" not in result.output


def test_audit_clear(runner, store_path, tmp_path):
    store_dir = str(tmp_path)
    log_event(store_dir, "set", "X")
    env = {"ENVCHAIN_STORE": str(tmp_path / "store.json"), "ENVCHAIN_PASSPHRASE": "pass"}
    result = runner.invoke(cli, ["audit-clear"], env=env, input="y\n", catch_exceptions=False)
    assert result.exit_code == 0
    assert "cleared" in result.output
