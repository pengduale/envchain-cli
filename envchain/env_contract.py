"""Contract enforcement for environment variables.

A contract defines expected type, format, and constraints for a key.
Contracts are stored as JSON metadata alongside the encrypted store.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


def _contract_path(store_path: str) -> Path:
    return Path(store_path).parent / "contracts.json"


def _load_contracts(store_path: str) -> dict:
    p = _contract_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_contracts(store_path: str, data: dict) -> None:
    _contract_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ContractResult:
    ok: bool
    key: str
    message: str

    def __repr__(self) -> str:
        status = "OK" if self.ok else "FAIL"
        return f"ContractResult({status}, {self.key!r}: {self.message})"


VALID_TYPES = {"string", "integer", "boolean", "float"}


def set_contract(
    store_path: str,
    key: str,
    *,
    value_type: str = "string",
    pattern: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    required: bool = True,
) -> ContractResult:
    if value_type not in VALID_TYPES:
        return ContractResult(False, key, f"Invalid type '{value_type}'. Must be one of {sorted(VALID_TYPES)}.")
    data = _load_contracts(store_path)
    data[key] = {
        "type": value_type,
        "pattern": pattern,
        "min_length": min_length,
        "max_length": max_length,
        "required": required,
    }
    _save_contracts(store_path, data)
    return ContractResult(True, key, "Contract set.")


def get_contract(store_path: str, key: str) -> Optional[dict]:
    return _load_contracts(store_path).get(key)


def remove_contract(store_path: str, key: str) -> bool:
    data = _load_contracts(store_path)
    if key not in data:
        return False
    del data[key]
    _save_contracts(store_path, data)
    return True


def enforce_contract(store_path: str, key: str, value: str) -> ContractResult:
    contract = get_contract(store_path, key)
    if contract is None:
        return ContractResult(True, key, "No contract defined.")

    if contract["required"] and not value:
        return ContractResult(False, key, "Value is required but empty.")

    vtype = contract["type"]
    if vtype == "integer":
        try:
            int(value)
        except ValueError:
            return ContractResult(False, key, f"Expected integer, got '{value}'.")
    elif vtype == "float":
        try:
            float(value)
        except ValueError:
            return ContractResult(False, key, f"Expected float, got '{value}'.")
    elif vtype == "boolean":
        if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            return ContractResult(False, key, f"Expected boolean, got '{value}'.")

    min_len = contract.get("min_length")
    max_len = contract.get("max_length")
    if min_len is not None and len(value) < min_len:
        return ContractResult(False, key, f"Value too short (min {min_len}).")
    if max_len is not None and len(value) > max_len:
        return ContractResult(False, key, f"Value too long (max {max_len}).")

    pattern = contract.get("pattern")
    if pattern and not re.fullmatch(pattern, value):
        return ContractResult(False, key, f"Value does not match pattern '{pattern}'.")

    return ContractResult(True, key, "Contract satisfied.")


def list_contracts(store_path: str) -> dict:
    return _load_contracts(store_path)
