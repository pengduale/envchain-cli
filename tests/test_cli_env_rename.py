"""Tests for CLI rename commands."""
import pytest
from click.testing import CliRunner
import click
from envchain.store import set_variable, get_variable
from envchain.profile import set_profile_variable, get_profile_variable
from envchain.cli_env_rename import register_rename_commands

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
    def root():
        pass
    register_rename_commands(root, lambda: store_path)
    return root


def invoke(runner, cli, args, passphrase=PASS):
    env = {"ENVCHAIN_PASSPHRASE": passphrase}
    return runner.invoke(cli, args, env=env, catch_exceptions=False)


def test_rename_run_success(runner, cli, store_path):
    set_variable(store_path, "FOO", "bar", PASS)
    result = invoke(runner, cli, ["rename", "run", "FOO", "BAR"])
    assert result.exit_code == 0
    assert "FOO -> BAR" in result.output
    assert get_variable(store_path, "BAR", PASS) == "bar"


def test_rename_run_missing(runner, cli, store_path):
    result = invoke(runner, cli, ["rename", "run", "MISSING", "NEW"])
    assert result.exit_code != 0


def test_rename_run_with_profile(runner, cli, store_path):
    set_profile_variable(store_path, "prod", "OLD", "val", PASS)
    result = invoke(runner, cli, ["rename", "run", "OLD", "NEW", "--profile", "prod"])
    assert result.exit_code == 0
    assert get_profile_variable(store_path, "prod", "NEW", PASS) == "val"


def test_rename_all_profiles(runner, cli, store_path):
    for p in ["dev", "staging"]:
        set_profile_variable(store_path, p, "KEY", "v", PASS)
    result = invoke(runner, cli, ["rename", "all-profiles", "KEY", "KEY2"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "staging" in result.output
