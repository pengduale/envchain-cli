import pytest
from click.testing import CliRunner
import click
from envchain.cli_env_promote import register_promote_commands
from envchain.profile import set_profile_variable, get_profile_variable

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

    register_promote_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_promote_run_basic(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "KEY1", "val1", PASS)
    result = invoke(runner, cli, ["promote", "run", "dev", "prod", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "ok" in result.output
    assert get_profile_variable(store_path, "prod", "KEY1", PASS) == "val1"


def test_promote_run_skip_existing(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "KEY1", "dev-val", PASS)
    set_profile_variable(store_path, "prod", "KEY1", "prod-val", PASS)
    result = invoke(runner, cli, ["promote", "run", "dev", "prod", "--passphrase", PASS])
    assert "skip" in result.output
    assert get_profile_variable(store_path, "prod", "KEY1", PASS) == "prod-val"


def test_promote_run_overwrite(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "KEY1", "new-val", PASS)
    set_profile_variable(store_path, "prod", "KEY1", "old-val", PASS)
    result = invoke(runner, cli, ["promote", "run", "dev", "prod", "--overwrite", "--passphrase", PASS])
    assert "ok" in result.output
    assert get_profile_variable(store_path, "prod", "KEY1", PASS) == "new-val"


def test_promote_one(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "SECRET", "s3cr3t", PASS)
    result = invoke(runner, cli, ["promote", "one", "SECRET", "dev", "prod", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "Promoted" in result.output


def test_promote_empty_source(runner, cli, store_path):
    result = invoke(runner, cli, ["promote", "run", "ghost", "prod", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "No variables" in result.output
