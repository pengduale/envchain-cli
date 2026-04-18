"""Tests for envchain.cli_template."""
import pytest
from pathlib import Path
from click.testing import CliRunner
import click

from envchain.store import set_variable
from envchain.cli_template import register_template_commands


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "store.json"
    set_variable(p, "pass", "API_KEY", "abc123")
    set_variable(p, "pass", "REGION", "us-east-1")
    return p


@pytest.fixture
def invoke(runner, store_path):
    @click.group()
    def cli():
        pass

    def get_store(ctx):
        return store_path, "pass"

    register_template_commands(cli, get_store)

    def _invoke(*args):
        return runner.invoke(cli, list(args))

    return _invoke


def test_render_stdout(invoke, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("key={{API_KEY}} region={{REGION}}")
    result = invoke("template", "render", str(tpl))
    assert result.exit_code == 0
    assert "abc123" in result.output
    assert "us-east-1" in result.output


def test_render_to_file(invoke, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{API_KEY}}")
    out = tmp_path / "out.txt"
    result = invoke("template", "render", str(tpl), "-o", str(out))
    assert result.exit_code == 0
    assert out.read_text() == "abc123"


def test_render_missing_var(invoke, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{UNDEFINED}}")
    result = invoke("template", "render", str(tpl))
    assert result.exit_code != 0
    assert "UNDEFINED" in result.output


def test_inspect_lists_vars(invoke, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("{{API_KEY}} and {{REGION}}")
    result = invoke("template", "inspect", str(tpl))
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "REGION" in result.output


def test_inspect_no_placeholders(invoke, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("nothing here")
    result = invoke("template", "inspect", str(tpl))
    assert result.exit_code == 0
    assert "No placeholders" in result.output
