"""Tests for CLI maturity commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
import click

from envchain.cli_env_maturity import register_maturity_commands
from envchain.env_maturity import set_maturity


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / "store.json"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)
        ctx.obj["store"] = store_path

    def get_store(ctx):
        return ctx.obj["store"]

    register_maturity_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_maturity_set(runner, cli):
    result = invoke(runner, cli, "maturity", "set", "API_KEY", "stable")
    assert result.exit_code == 0
    assert "stable" in result.output


def test_maturity_set_with_note(runner, cli):
    result = invoke(runner, cli, "maturity", "set", "DB_PASS", "beta", "--note", "Under review")
    assert result.exit_code == 0
    assert "Under review" in result.output


def test_maturity_get(runner, cli, store_path):
    set_maturity(store_path, "TOKEN", "experimental", note="Draft")
    result = invoke(runner, cli, "maturity", "get", "TOKEN")
    assert result.exit_code == 0
    assert "experimental" in result.output
    assert "Draft" in result.output


def test_maturity_get_missing(runner, cli):
    result = runner.invoke(cli, ["maturity", "get", "GHOST"])
    assert result.exit_code != 0
    assert "No maturity level" in result.output


def test_maturity_remove(runner, cli, store_path):
    set_maturity(store_path, "OLD_KEY", "deprecated")
    result = invoke(runner, cli, "maturity", "remove", "OLD_KEY")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_maturity_remove_missing(runner, cli):
    result = runner.invoke(cli, ["maturity", "remove", "NONEXISTENT"])
    assert result.exit_code != 0


def test_maturity_list_empty(runner, cli):
    result = invoke(runner, cli, "maturity", "list")
    assert result.exit_code == 0
    assert "No maturity levels" in result.output


def test_maturity_list_with_filter(runner, cli, store_path):
    set_maturity(store_path, "A", "stable")
    set_maturity(store_path, "B", "beta")
    result = invoke(runner, cli, "maturity", "list", "--filter", "stable")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output
