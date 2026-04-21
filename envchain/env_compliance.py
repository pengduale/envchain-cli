"""Compliance checking for environment variables against defined rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envchain.store import list_keys, get_variable


@dataclass
class ComplianceResult:
    key: str
    passed: bool
    rule: str
    message: str

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"ComplianceResult({status}, key={self.key!r}, rule={self.rule!r})"


REQUIRED_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


def check_key_naming(key: str) -> ComplianceResult:
    """Ensure the key follows UPPER_SNAKE_CASE convention."""
    passed = bool(REQUIRED_PATTERN.match(key))
    return ComplianceResult(
        key=key,
        passed=passed,
        rule="key_naming",
        message="OK" if passed else f"Key '{key}' must match UPPER_SNAKE_CASE.",
    )


def check_value_not_empty(key: str, store_path: Path, passphrase: str) -> ComplianceResult:
    """Ensure the stored value is not empty."""
    value = get_variable(store_path, key, passphrase)
    passed = bool(value and value.strip())
    return ComplianceResult(
        key=key,
        passed=passed,
        rule="value_not_empty",
        message="OK" if passed else f"Key '{key}' has an empty or missing value.",
    )


def check_value_min_length(
    key: str, store_path: Path, passphrase: str, min_length: int = 8
) -> ComplianceResult:
    """Ensure the stored value meets a minimum length."""
    value = get_variable(store_path, key, passphrase) or ""
    passed = len(value) >= min_length
    return ComplianceResult(
        key=key,
        passed=passed,
        rule="value_min_length",
        message="OK" if passed else f"Key '{key}' value is shorter than {min_length} chars.",
    )


def run_compliance(
    store_path: Path,
    passphrase: str,
    min_length: int = 8,
    keys: Optional[List[str]] = None,
) -> List[ComplianceResult]:
    """Run all compliance checks for all (or specified) keys in the store."""
    target_keys = keys if keys is not None else list_keys(store_path)
    results: List[ComplianceResult] = []
    for key in target_keys:
        results.append(check_key_naming(key))
        results.append(check_value_not_empty(key, store_path, passphrase))
        results.append(check_value_min_length(key, store_path, passphrase, min_length))
    return results


def compliance_summary(results: List[ComplianceResult]) -> dict:
    """Return a summary dict with total, passed, and failed counts."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return {"total": total, "passed": passed, "failed": total - passed}
