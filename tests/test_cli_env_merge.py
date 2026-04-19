import pytest
from click.testing import CliRunner
import click
from envchain.env_merge import merge_profiles
from envchain.profile import set_profile_variable, get_profile_variable
from envchain.cli_env_merge import register_merge_commands

PASS = "testpass"


@pytest.fixture
def store_path(tmp_path):
    return str(tmp_path)


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

    register_merge_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def _set(store_path, profile, key, value):
    set_profile_variable(store_path, profile, key, value, PASS)


def test_merge_run_copies(runner, cli, store_path):
    _set(store_path, "dev", "API_KEY", "abc")
    result = invoke(runner, cli, ["merge", "run", "dev", "--target", "staging", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "copied" in result.output
    val = get_profile_variable(store_path, "staging", "API_KEY", PASS)
    assert val == "abc"


def test_merge_run_empty(runner, cli, store_path):
    result = invoke(runner, cli, ["merge", "run", "empty", "--target", "prod", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "Nothing" in result.output


def test_merge_summary_command(runner, cli, store_path):
    _set(store_path, "dev", "X", "1")
    _set(store_path, "staging", "X", "old")
    result = invoke(runner, cli, ["merge", "summary", "dev", "--target", "staging", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "skip" in result.output


def test_merge_run_overwrite_flag(runner, cli, store_path):
    _set(store_path, "dev", "K", "new")
    _set(store_path, "staging", "K", "old")
    result = invoke(runner, cli, ["merge", "run", "dev", "--target", "staging", "--passphrase", PASS, "--overwrite"])
    assert result.exit_code == 0
    assert "overwritten" in result.output
    assert get_profile_variable(store_path, "staging", "K", PASS) == "new"
