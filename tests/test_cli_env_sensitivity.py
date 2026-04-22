"""Tests for the sensitivity CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
import click

from envchain.cli_env_sensitivity import register_sensitivity_commands
from envchain.env_sensitivity import set_sensitivity


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "store.json"
    p.write_text("{}")
    return p


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

    register_sensitivity_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_sensitivity_set(runner, cli):
    result = invoke(runner, cli, ["sensitivity", "set", "DB_PASS", "critical"])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_sensitivity_get(runner, cli, store_path):
    set_sensitivity(store_path, "API_KEY", "high")
    result = invoke(runner, cli, ["sensitivity", "get", "API_KEY"])
    assert result.exit_code == 0
    assert "high" in result.output


def test_sensitivity_get_missing(runner, cli):
    result = invoke(runner, cli, ["sensitivity", "get", "MISSING"])
    assert result.exit_code == 0
    assert "No sensitivity level" in result.output


def test_sensitivity_remove(runner, cli, store_path):
    set_sensitivity(store_path, "TOKEN", "medium")
    result = invoke(runner, cli, ["sensitivity", "remove", "TOKEN"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_sensitivity_list_empty(runner, cli):
    result = invoke(runner, cli, ["sensitivity", "list"])
    assert result.exit_code == 0
    assert "No sensitivity levels" in result.output


def test_sensitivity_list_with_entries(runner, cli, store_path):
    set_sensitivity(store_path, "A", "low")
    set_sensitivity(store_path, "B", "critical")
    result = invoke(runner, cli, ["sensitivity", "list"])
    assert result.exit_code == 0
    assert "A: low" in result.output
    assert "B: critical" in result.output


def test_sensitivity_list_filter_by_level(runner, cli, store_path):
    set_sensitivity(store_path, "X", "high")
    set_sensitivity(store_path, "Y", "low")
    result = invoke(runner, cli, ["sensitivity", "list", "--level", "high"])
    assert result.exit_code == 0
    assert "X" in result.output
    assert "Y" not in result.output
