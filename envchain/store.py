"""Read and write the encrypted .envchain store file (JSON-based)."""

import json
from pathlib import Path
from typing import Dict

from envchain.crypto import encrypt, decrypt

DEFAULT_STORE_FILE = ".envchain"


def _load_raw(store_path: Path) -> Dict[str, str]:
    if not store_path.exists():
        return {}
    with store_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_raw(store_path: Path, data: Dict[str, str]) -> None:
    with store_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def set_variable(key: str, value: str, passphrase: str, store_path: Path) -> None:
    """Encrypt and store an environment variable."""
    data = _load_raw(store_path)
    data[key] = encrypt(value, passphrase)
    _save_raw(store_path, data)


def get_variable(key: str, passphrase: str, store_path: Path) -> str:
    """Retrieve and decrypt an environment variable."""
    data = _load_raw(store_path)
    if key not in data:
        raise KeyError(f"Variable '{key}' not found in store.")
    return decrypt(data[key], passphrase)


def delete_variable(key: str, store_path: Path) -> None:
    """Remove a variable from the store (no passphrase needed)."""
    data = _load_raw(store_path)
    if key not in data:
        raise KeyError(f"Variable '{key}' not found in store.")
    del data[key]
    _save_raw(store_path, data)


def list_keys(store_path: Path) -> list:
    """Return all stored variable names."""
    return sorted(_load_raw(store_path).keys())
