"""Tests for cli_env_copy commands."""
import pytest
from pathlib import Path
from click.testing import CliRunner
import click

from envchain.profile import set_profile_variable, get_profile_variable
from envchain.store import set_variable
from envchain.cli_env_copy import register_env_copy_commands

PASS = "testpass"


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / ".envchain"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)

    def get_store(ctx):
        return store_path

    register_env_copy_commands(root, get_store)
    return root


def invoke(runner, cli, args, input=None):
    return runner.invoke(cli, args, input=input, catch_exceptions=False)


def test_copy_profile_command(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "MY_VAR", "hello", PASS)
    result = invoke(runner, cli, ["copy", "profile", "dev", "staging", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "+ MY_VAR" in result.output
    assert get_profile_variable(store_path, "staging", "MY_VAR", PASS) == "hello"


def test_copy_profile_skip_existing(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "K", "new", PASS)
    set_profile_variable(store_path, "prod", "K", "old", PASS)
    result = invoke(runner, cli, ["copy", "profile", "dev", "prod", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "skipped" in result.output
    assert get_profile_variable(store_path, "prod", "K", PASS) == "old"


def test_copy_to_profile_command(runner, cli, store_path):
    set_variable(store_path, "SEC", "value", PASS)
    result = invoke(runner, cli, ["copy", "to-profile", "ci", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "+ SEC" in result.output
    assert get_profile_variable(store_path, "ci", "SEC", PASS) == "value"


def test_copy_profile_overwrite_flag(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "X", "updated", PASS)
    set_profile_variable(store_path, "prod", "X", "stale", PASS)
    result = invoke(runner, cli, ["copy", "profile", "dev", "prod", "--passphrase", PASS, "--overwrite"])
    assert result.exit_code == 0
    assert "~ X" in result.output
    assert get_profile_variable(store_path, "prod", "X", PASS) == "updated"
