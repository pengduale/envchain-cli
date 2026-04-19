"""Validate stored environment variables against a schema."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from envchain.store import get_variable, list_keys


@dataclass
class ValidationRule:
    key: str
    required: bool = True
    pattern: Optional[str] = None
    min_length: int = 0
    max_length: int = 0  # 0 = unlimited
    allowed_values: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    key: str
    passed: bool
    message: str


def validate_variable(store_path: str, passphrase: str, rule: ValidationRule) -> ValidationResult:
    value = get_variable(store_path, passphrase, rule.key)

    if value is None:
        if rule.required:
            return ValidationResult(rule.key, False, "required key is missing")
        return ValidationResult(rule.key, True, "optional key absent")

    if rule.min_length and len(value) < rule.min_length:
        return ValidationResult(rule.key, False, f"value too short (min {rule.min_length})")

    if rule.max_length and len(value) > rule.max_length:
        return ValidationResult(rule.key, False, f"value too long (max {rule.max_length})")

    if rule.pattern and not re.fullmatch(rule.pattern, value):
        return ValidationResult(rule.key, False, f"value does not match pattern '{rule.pattern}'")

    if rule.allowed_values and value not in rule.allowed_values:
        return ValidationResult(rule.key, False, f"value not in allowed set {rule.allowed_values}")

    return ValidationResult(rule.key, True, "ok")


def validate_all(store_path: str, passphrase: str, rules: List[ValidationRule]) -> List[ValidationResult]:
    return [validate_variable(store_path, passphrase, r) for r in rules]


def load_schema(schema: Dict[str, Any]) -> List[ValidationRule]:
    """Build rules from a plain dict schema."""
    rules = []
    for key, opts in schema.items():
        rules.append(ValidationRule(
            key=key,
            required=opts.get("required", True),
            pattern=opts.get("pattern"),
            min_length=opts.get("min_length", 0),
            max_length=opts.get("max_length", 0),
            allowed_values=opts.get("allowed_values", []),
        ))
    return rules
