"""Tests for envchain.lint module."""

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.lint import lint_store, LintIssue

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "test.env.enc")


def test_lint_empty_store_no_issues(store):
    issues = lint_store(store, PASS)
    assert issues == []


def test_lint_valid_key_no_issues(store):
    set_variable(store, "DATABASE_URL", "postgres://localhost/db", PASS)
    issues = lint_store(store, PASS)
    assert all(i.key != "DATABASE_URL" or i.level != "error" for i in issues)


def test_lint_lowercase_key_warns(store):
    set_variable(store, "my_var", "value", PASS)
    issues = lint_store(store, PASS)
    keys_warned = [i.key for i in issues if i.level == "warning"]
    assert "my_var" in keys_warned


def test_lint_mixed_case_key_warns(store):
    set_variable(store, "myVar", "value", PASS)
    issues = lint_store(store, PASS)
    assert any(i.key == "myVar" and "UPPER_SNAKE_CASE" in i.message for i in issues)


def test_lint_empty_value_warns(store):
    set_variable(store, "SOME_KEY", "   ", PASS)
    issues = lint_store(store, PASS)
    assert any(i.key == "SOME_KEY" and "empty" in i.message for i in issues)


def test_lint_short_secret_value_errors(store):
    set_variable(store, "API_TOKEN", "ab", PASS)
    issues = lint_store(store, PASS)
    assert any(i.key == "API_TOKEN" and i.level == "error" for i in issues)


def test_lint_returns_lint_issue_instances(store):
    set_variable(store, "bad key", "val", PASS)
    issues = lint_store(store, PASS)
    assert all(isinstance(i, LintIssue) for i in issues)


def test_lint_multiple_keys(store):
    set_variable(store, "GOOD_KEY", "goodvalue", PASS)
    set_variable(store, "badkey", "v", PASS)
    issues = lint_store(store, PASS)
    issue_keys = {i.key for i in issues}
    assert "badkey" in issue_keys
