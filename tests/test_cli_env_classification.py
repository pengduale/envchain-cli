"""Tests for envchain.cli_env_classification."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
import click

from envchain.cli_env_classification import register_classification_commands


@pytest.fixture()
def store_path(tmp_path):
    return str(tmp_path / "store.json")


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)
        ctx.obj["store"] = store_path

    def get_store(ctx):
        return ctx.obj["store"]

    register_classification_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_set_and_get(runner, cli):
    result = invoke(runner, cli, "classification", "set", "API_KEY", "secret")
    assert result.exit_code == 0
    assert "secret" in result.output

    result = invoke(runner, cli, "classification", "get", "API_KEY")
    assert result.exit_code == 0
    assert "secret" in result.output


def test_get_missing(runner, cli):
    result = invoke(runner, cli, "classification", "get", "MISSING")
    assert result.exit_code == 0
    assert "No classification" in result.output


def test_remove(runner, cli):
    invoke(runner, cli, "classification", "set", "TOKEN", "internal")
    result = invoke(runner, cli, "classification", "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing(runner, cli):
    result = invoke(runner, cli, "classification", "remove", "GHOST")
    assert result.exit_code == 0
    assert "No classification found" in result.output


def test_list_empty(runner, cli):
    result = invoke(runner, cli, "classification", "list")
    assert result.exit_code == 0
    assert "No classifications" in result.output


def test_list_multiple(runner, cli):
    invoke(runner, cli, "classification", "set", "A", "public")
    invoke(runner, cli, "classification", "set", "B", "confidential")
    result = invoke(runner, cli, "classification", "list")
    assert "A: public" in result.output
    assert "B: confidential" in result.output
