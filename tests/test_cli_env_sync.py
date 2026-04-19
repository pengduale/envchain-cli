import pytest
from click.testing import CliRunner
from click import group
from pathlib import Path
from envchain.cli_env_sync import register_sync_commands
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
    @group()
    def root():
        pass

    def get_store():
        return store_path

    register_sync_commands(root, get_store)
    return root


def invoke(runner, cli, args, input=None):
    return runner.invoke(cli, args, input=input, catch_exceptions=False)


def test_sync_profiles_command(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "KEY", "value", PASS)
    result = invoke(runner, cli, ["sync", "profiles", "dev", "staging", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "Copied:" in result.output
    assert get_profile_variable(store_path, "staging", "KEY", PASS) == "value"


def test_sync_profiles_skip_message(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "KEY", "new", PASS)
    set_profile_variable(store_path, "staging", "KEY", "old", PASS)
    result = invoke(runner, cli, ["sync", "profiles", "dev", "staging", "--passphrase", PASS])
    assert "skipped" in result.output


def test_sync_to_default_command(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "MY_VAR", "hello", PASS)
    result = invoke(runner, cli, ["sync", "to-default", "dev", "--passphrase", PASS])
    assert result.exit_code == 0
    assert "Copied:" in result.output


def test_sync_profiles_overwrite_flag(runner, cli, store_path):
    set_profile_variable(store_path, "dev", "KEY", "updated", PASS)
    set_profile_variable(store_path, "staging", "KEY", "old", PASS)
    result = invoke(runner, cli, ["sync", "profiles", "dev", "staging", "--passphrase", PASS, "--overwrite"])
    assert "Overwritten:" in result.output
    assert get_profile_variable(store_path, "staging", "KEY", PASS) == "updated"
