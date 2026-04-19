"""Check required environment variables are set and valid."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re

from envchain.store import get_variable, list_keys


@dataclass
class CheckResult:
    key: str
    present: bool
    valid: bool
    message: str = ""


@dataclass
class CheckRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None
    min_length: int = 0


def check_variable(store_path: str, passphrase: str, rule: CheckRule) -> CheckResult:
    try:
        value = get_variable(store_path, rule.key, passphrase)
    except Exception:
        value = None

    if value is None:
        if rule.required:
            return CheckResult(rule.key, present=False, valid=False, message="missing required variable")
        return CheckResult(rule.key, present=False, valid=True, message="optional, not set")

    if rule.min_length and len(value) < rule.min_length:
        return CheckResult(rule.key, present=True, valid=False,
                           message=f"value shorter than minimum length {rule.min_length}")

    if rule.pattern and not re.fullmatch(rule.pattern, value):
        return CheckResult(rule.key, present=True, valid=False,
                           message=f"value does not match pattern '{rule.pattern}'")

    return CheckResult(rule.key, present=True, valid=True)


def check_all(store_path: str, passphrase: str, rules: list[CheckRule]) -> list[CheckResult]:
    return [check_variable(store_path, passphrase, rule) for rule in rules]


def check_keys_exist(store_path: str, passphrase: str, keys: list[str]) -> list[CheckResult]:
    rules = [CheckRule(key=k) for k in keys]
    return check_all(store_path, passphrase, rules)
