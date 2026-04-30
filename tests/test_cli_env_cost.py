"""CLI tests for env cost commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path
import click

from envchain.cli_env_cost import register_cost_commands
from envchain.env_cost import set_cost


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / "store.json"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    def root():
        pass

    def get_store(ctx):
        return store_path

    register_cost_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_cost_set_basic(runner, cli):
    result = invoke(runner, cli, ["cost", "set", "OPENAI_KEY", "0.02"])
    assert result.exit_code == 0
    assert "OPENAI_KEY" in result.output
    assert "0.02" in result.output


def test_cost_set_with_currency_and_note(runner, cli):
    result = invoke(runner, cli, ["cost", "set", "STRIPE_KEY", "0.30", "--currency", "EUR", "--note", "per call"])
    assert result.exit_code == 0
    assert "EUR" in result.output
    assert "per call" in result.output


def test_cost_set_invalid_currency(runner, cli):
    result = runner.invoke(cli, ["cost", "set", "KEY", "1.0", "--currency", "ZZZ"])
    assert "Error" in result.output or result.exit_code != 0


def test_cost_get_after_set(runner, cli, store_path):
    set_cost(store_path, "MY_KEY", 5.0, "USD", note="test note")
    result = invoke(runner, cli, ["cost", "get", "MY_KEY"])
    assert "5.0" in result.output
    assert "USD" in result.output
    assert "test note" in result.output


def test_cost_get_missing(runner, cli):
    result = invoke(runner, cli, ["cost", "get", "MISSING"])
    assert "No cost metadata" in result.output


def test_cost_remove(runner, cli, store_path):
    set_cost(store_path, "DEL_KEY", 1.0, "USD")
    result = invoke(runner, cli, ["cost", "remove", "DEL_KEY"])
    assert "Removed" in result.output


def test_cost_remove_missing(runner, cli):
    result = invoke(runner, cli, ["cost", "remove", "GHOST"])
    assert "No cost metadata" in result.output


def test_cost_list_empty(runner, cli):
    result = invoke(runner, cli, ["cost", "list"])
    assert "No cost metadata" in result.output


def test_cost_list_multiple(runner, cli, store_path):
    set_cost(store_path, "KEY_A", 1.0, "USD")
    set_cost(store_path, "KEY_B", 2.0, "EUR")
    result = invoke(runner, cli, ["cost", "list"])
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output
