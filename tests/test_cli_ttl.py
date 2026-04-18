"""Tests for CLI TTL commands."""
import time
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
import click

from envchain.cli_ttl import register_ttl_commands
from envchain.ttl import set_ttl, get_expiry


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / "vars.env.json"


@pytest.fixture
def invoke(runner, store_path):
    @click.group()
    def cli():
        pass

    def get_store(ctx):
        return store_path

    register_ttl_commands(cli, get_store)

    def _invoke(*args, **kwargs):
        return runner.invoke(cli, *args, **kwargs)

    return _invoke


def test_ttl_set(invoke, store_path):
    result = invoke(["ttl", "set", "MY_KEY", "300"])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert get_expiry(store_path, "MY_KEY") is not None


def test_ttl_get_no_ttl(invoke):
    result = invoke(["ttl", "get", "UNSET"])
    assert result.exit_code == 0
    assert "no TTL set" in result.output


def test_ttl_get_with_ttl(invoke, store_path):
    set_ttl(store_path, "FOO", 120)
    result = invoke(["ttl", "get", "FOO"])
    assert result.exit_code == 0
    assert "remaining" in result.output


def test_ttl_get_expired(invoke, store_path):
    set_ttl(store_path, "OLD", -5)
    result = invoke(["ttl", "get", "OLD"])
    assert result.exit_code == 0
    assert "expired" in result.output


def test_ttl_clear(invoke, store_path):
    set_ttl(store_path, "BAR", 60)
    result = invoke(["ttl", "clear", "BAR"])
    assert result.exit_code == 0
    assert get_expiry(store_path, "BAR") is None


def test_ttl_purge_no_expired(invoke, store_path):
    result = invoke(["ttl", "purge", "--passphrase", "secret"])
    assert result.exit_code == 0
    assert "No expired" in result.output
