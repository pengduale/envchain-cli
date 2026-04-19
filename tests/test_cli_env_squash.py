import pytest
from click.testing import CliRunner
import click
from envchain.cli_env_squash import register_squash_commands
from envchain.profile import set_profile_variable, get_profile_variable

PASS = "testpass"


@pytest.fixture
def store_path(tmp_path):
    return tmp_path


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
        ctx.obj["passphrase"] = PASS

    def get_store(ctx):
        return ctx.obj["store"]

    register_squash_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_squash_basic(runner, cli, store_path):
    set_profile_variable(store_path, PASS, "dev", "KEY1", "v1")
    set_profile_variable(store_path, PASS, "staging", "KEY2", "v2")
    result = invoke(runner, cli, ["squash", "run", "dev", "staging", "--dest", "merged"])
    assert result.exit_code == 0
    assert "wrote" in result.output
    assert get_profile_variable(store_path, PASS, "merged", "KEY1") == "v1"
    assert get_profile_variable(store_path, PASS, "merged", "KEY2") == "v2"


def test_squash_reports_skipped(runner, cli, store_path):
    set_profile_variable(store_path, PASS, "dev", "KEY1", "new")
    set_profile_variable(store_path, PASS, "merged", "KEY1", "old")
    result = invoke(runner, cli, ["squash", "run", "dev", "--dest", "merged"])
    assert "skipped" in result.output
    assert get_profile_variable(store_path, PASS, "merged", "KEY1") == "old"


def test_squash_overwrite_flag(runner, cli, store_path):
    set_profile_variable(store_path, PASS, "dev", "KEY1", "updated")
    set_profile_variable(store_path, PASS, "merged", "KEY1", "old")
    result = invoke(runner, cli, ["squash", "run", "dev", "--dest", "merged", "--overwrite"])
    assert result.exit_code == 0
    assert get_profile_variable(store_path, PASS, "merged", "KEY1") == "updated"
