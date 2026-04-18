import re
from dataclasses import dataclass
from typing import List
from envchain.store import list_keys, get_variable


@dataclass
class LintIssue:
    key: str
    level: str  # 'error' or 'warning'
    message: str


def _check_key(key: str) -> List[LintIssue]:
    issues = []
    if not key:
        issues.append(LintIssue(key=key, level="error", message="Key must not be empty."))
        return issues
    if key != key.upper():
        issues.append(LintIssue(key=key, level="warning", message="Key should be uppercase."))
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
        issues.append(LintIssue(key=key, level="error", message="Key contains invalid characters."))
    if key.startswith("_"):
        issues.append(LintIssue(key=key, level="warning", message="Key starts with underscore."))
    return issues


def _check_value(key: str, value: str) -> List[LintIssue]:
    issues = []
    if not value or not value.strip():
        issues.append(LintIssue(key=key, level="warning", message="Value is empty or blank."))
    if len(value) > 4096:
        issues.append(LintIssue(key=key, level="warning", message="Value exceeds 4096 characters."))
    return issues


def lint_store(store_path: str, passphrase: str) -> List[LintIssue]:
    issues = []
    keys = list_keys(store_path)
    for key in keys:
        issues.extend(_check_key(key))
        try:
            value = get_variable(store_path, key, passphrase)
            issues.extend(_check_value(key, value))
        except Exception as e:
            issues.append(LintIssue(key=key, level="error", message=f"Could not decrypt value: {e}"))
    return issues
