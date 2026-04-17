"""Tests for envchain.export module."""

import pytest
from envchain.export import export_to_shell, export_to_dotenv, parse_dotenv


SAMPLE = {"DB_URL": "postgres://localhost/db", "SECRET": "p@ss w0rd!", "DEBUG": "1"}


def test_export_shell_contains_export():
    result = export_to_shell(SAMPLE)
    assert result.count("export ") == 3


def test_export_shell_quotes_special_chars():
    result = export_to_shell({"K": "hello world"})
    assert "'hello world'" in result or '"hello world"' in result or "hello\\ world" in result


def test_export_fish_format():
    result = export_to_shell({"FOO": "bar"}, shell="fish")
    assert result.startswith("set -x FOO")
    assert "export" not in result


def test_export_dotenv_format():
    result = export_to_dotenv({"KEY": "value"})
    assert 'KEY="value"' in result


def test_export_dotenv_escapes_quotes():
    result = export_to_dotenv({"MSG": 'say "hi"'})
    assert '\\"' in result


def test_parse_dotenv_basic():
    content = 'FOO=bar\nBAZ="qux"\n'
    result = parse_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_dotenv_ignores_comments():
    content = "# comment\nKEY=val\n"
    result = parse_dotenv(content)
    assert "KEY" in result
    assert len(result) == 1


def test_parse_dotenv_ignores_blank_lines():
    content = "\n\nA=1\n\nB=2\n"
    result = parse_dotenv(content)
    assert result == {"A": "1", "B": "2"}


def test_parse_dotenv_single_quoted():
    content = "TOKEN='abc123'"
    result = parse_dotenv(content)
    assert result["TOKEN"] == "abc123"


def test_roundtrip_dotenv():
    original = {"X": "hello", "Y": "world"}
    content = export_to_dotenv(original)
    parsed = parse_dotenv(content)
    assert parsed == original
