"""Tests for envchain.env_workflow."""
import pytest
from pathlib import Path
from envchain.env_workflow import (
    create_workflow,
    get_workflow,
    delete_workflow,
    list_workflows,
    validate_workflow,
)


@pytest.fixture
def store(tmp_path):
    p = tmp_path / "store.json"
    p.write_text("{}")
    return str(p)


def test_create_workflow_returns_ok(store):
    result = create_workflow(store, "onboarding", ["DB_URL", "API_KEY"])
    assert result.ok
    assert result.name == "onboarding"
    assert result.keys == ["DB_URL", "API_KEY"]


def test_get_workflow_after_create(store):
    create_workflow(store, "deploy", ["AWS_KEY", "AWS_SECRET"])
    keys = get_workflow(store, "deploy")
    assert keys == ["AWS_KEY", "AWS_SECRET"]


def test_get_missing_workflow_returns_none(store):
    assert get_workflow(store, "nonexistent") is None


def test_create_workflow_empty_name_fails(store):
    result = create_workflow(store, "", ["KEY"])
    assert not result.ok
    assert "empty" in result.message.lower()


def test_create_workflow_empty_keys_fails(store):
    result = create_workflow(store, "empty_wf", [])
    assert not result.ok
    assert "at least one key" in result.message.lower()


def test_delete_workflow_returns_true(store):
    create_workflow(store, "temp", ["X"])
    assert delete_workflow(store, "temp") is True
    assert get_workflow(store, "temp") is None


def test_delete_missing_workflow_returns_false(store):
    assert delete_workflow(store, "ghost") is False


def test_list_workflows_empty(store):
    assert list_workflows(store) == []


def test_list_workflows_multiple(store):
    create_workflow(store, "alpha", ["A"])
    create_workflow(store, "beta", ["B"])
    names = list_workflows(store)
    assert "alpha" in names
    assert "beta" in names


def test_validate_workflow_all_present(store):
    create_workflow(store, "check", ["DB_URL", "SECRET"])
    result = validate_workflow(store, "check", ["DB_URL", "SECRET", "EXTRA"])
    assert result.ok
    assert "present" in result.message.lower()


def test_validate_workflow_missing_keys(store):
    create_workflow(store, "check", ["DB_URL", "SECRET"])
    result = validate_workflow(store, "check", ["DB_URL"])
    assert not result.ok
    assert "SECRET" in result.message


def test_validate_workflow_not_found(store):
    result = validate_workflow(store, "missing_wf", ["A", "B"])
    assert not result.ok
    assert "not found" in result.message.lower()


def test_overwrite_workflow(store):
    create_workflow(store, "wf", ["A", "B"])
    create_workflow(store, "wf", ["C"])
    assert get_workflow(store, "wf") == ["C"]
