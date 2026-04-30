"""CLI tests for envchain risk commands."""
import pytest
from pathlib import Path
from click.testing import CliRunner
import click

from envchain.cli_env_risk import register_risk_commands
from envchain.env_risk import set_risk


@pytest.fixture
def store_path(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    def root():
        pass

    def get_store(ctx):
        return str(store_path)

    register_risk_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_risk_set_basic(runner, cli):
    result = invoke(runner, cli, ["risk", "set", "DB_PASS", "high"])
    assert result.exit_code == 0
    assert "high" in result.output


def test_risk_set_with_reason(runner, cli):
    result = invoke(runner, cli, ["risk", "set", "TOKEN", "critical", "--reason", "leaked"])
    assert result.exit_code == 0


def test_risk_get_existing(runner, cli, store_path):
    set_risk(store_path, "API_KEY", "medium", "third-party")
    result = invoke(runner, cli, ["risk", "get", "API_KEY"])
    assert "medium" in result.output
    assert "third-party" in result.output


def test_risk_get_missing(runner, cli):
    result = invoke(runner, cli, ["risk", "get", "UNKNOWN"])
    assert "No risk entry" in result.output


def test_risk_remove_existing(runner, cli, store_path):
    set_risk(store_path, "OLD_KEY", "low")
    result = invoke(runner, cli, ["risk", "remove", "OLD_KEY"])
    assert "removed" in result.output


def test_risk_remove_missing(runner, cli):
    result = invoke(runner, cli, ["risk", "remove", "GHOST"])
    assert "No risk entry found" in result.output


def test_risk_list_empty(runner, cli):
    result = invoke(runner, cli, ["risk", "list"])
    assert "No risk entries" in result.output


def test_risk_list_shows_entries(runner, cli, store_path):
    set_risk(store_path, "KEY_A", "low")
    set_risk(store_path, "KEY_B", "critical", "public")
    result = invoke(runner, cli, ["risk", "list"])
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output
    assert "critical" in result.output
