"""Integration tests for export/import CLI commands."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envchain.cli import cli


@pytest.fixture
def runner(tmp_path):
    return CliRunner()


@pytest.fixture
def store_path(tmp_path):
    return str(tmp_path / "test_store.json")


def invoke(runner, store_path, *args):
    return runner.invoke(cli, ["--store", store_path, "--passphrase", "testpass"] + list(args))


def test_export_empty_store(runner, store_path):
    result = invoke(runner, store_path, "export")
    assert result.exit_code == 0
    assert "No variables" in result.output


def test_export_shell_format(runner, store_path):
    invoke(runner, store_path, "set", "API_KEY", "secret123")
    result = invoke(runner, store_path, "export", "--format", "shell")
    assert result.exit_code == 0
    assert "export API_KEY" in result.output


def test_export_dotenv_format(runner, store_path):
    invoke(runner, store_path, "set", "MY_VAR", "hello")
    result = invoke(runner, store_path, "export", "--format", "dotenv")
    assert result.exit_code == 0
    assert 'MY_VAR="hello"' in result.output


def test_export_to_file(runner, store_path, tmp_path):
    invoke(runner, store_path, "set", "FOO", "bar")
    out_file = str(tmp_path / "out.env")
    result = invoke(runner, store_path, "export", "--format", "dotenv", "--output", out_file)
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "FOO" in content


def test_import_dotenv_file(runner, store_path, tmp_path):
    env_file = tmp_path / "import.env"
    env_file.write_text('IMPORTED_KEY="imported_value"\n')
    result = invoke(runner, store_path, "import", str(env_file))
    assert result.exit_code == 0
    assert "IMPORTED_KEY" in result.output
    get_result = invoke(runner, store_path, "get", "IMPORTED_KEY")
    assert "imported_value" in get_result.output


def test_import_skips_existing_without_overwrite(runner, store_path, tmp_path):
    invoke(runner, store_path, "set", "EXIST", "original")
    env_file = tmp_path / "import.env"
    env_file.write_text("EXIST=new_value\n")
    result = invoke(runner, store_path, "import", str(env_file))
    assert "Skipped" in result.output
    get_result = invoke(runner, store_path, "get", "EXIST")
    assert "original" in get_result.output


def test_import_overwrites_with_flag(runner, store_path, tmp_path):
    invoke(runner, store_path, "set", "EXIST", "original")
    env_file = tmp_path / "import.env"
    env_file.write_text("EXIST=updated\n")
    invoke(runner, store_path, "import", "--overwrite", str(env_file))
    get_result = invoke(runner, store_path, "get", "EXIST")
    assert "updated" in get_result.output
