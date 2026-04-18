"""Lint stored environment variable keys and values for common issues."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List
import re

from envchain.store import list_keys, get_variable


@dataclass
class LintIssue:
    key: str
    level: str  # 'warning' or 'error'
    message: str


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_COMMON_SECRETS = re.compile(r'(password|secret|token|key|passwd)', re.IGNORECASE)


def _check_key(key: str) -> List[LintIssue]:
    issues = []
    if not _VALID_KEY_RE.match(key):
        issues.append(LintIssue(key, 'warning', f'Key "{key}" is not UPPER_SNAKE_CASE'))
    if len(key) < 2:
        issues.append(LintIssue(key, 'error', f'Key "{key}" is too short'))
    return issues


def _check_value(key: str, value: str) -> List[LintIssue]:
    issues = []
    if not value.strip():
        issues.append(LintIssue(key, 'warning', f'Key "{key}" has an empty or whitespace-only value'))
    if len(value) < 4 and _COMMON_SECRETS.search(key):
        issues.append(LintIssue(key, 'error', f'Key "{key}" looks like a secret but has a very short value'))
    return issues


def lint_store(store_path: str, passphrase: str) -> List[LintIssue]:
    """Run all lint checks against a store. Returns list of issues found."""
    issues: List[LintIssue] = []
    keys = list_keys(store_path)
    if not keys:
        return issues
    for key in keys:
        issues.extend(_check_key(key))
        try:
            value = get_variable(store_path, key, passphrase)
            issues.extend(_check_value(key, value))
        except Exception:
            issues.append(LintIssue(key, 'error', f'Key "{key}" could not be decrypted'))
    return issues
