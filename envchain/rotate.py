"""Key rotation: re-encrypt all variables with a new passphrase."""

from __future__ import annotations

from pathlib import Path

from envchain.crypto import decrypt, encrypt
from envchain.store import _load_raw, _save_raw


def rotate_passphrase(store_path: Path, old_passphrase: str, new_passphrase: str) -> int:
    """Re-encrypt every variable in the store with a new passphrase.

    Returns the number of variables rotated.
    Raises ValueError if the store is empty.
    Raises cryptography.fernet.InvalidToken if old_passphrase is wrong.
    """
    data = _load_raw(store_path)

    if not data:
        raise ValueError("Store is empty – nothing to rotate.")

    rotated: dict[str, str] = {}
    for key, ciphertext in data.items():
        plaintext = decrypt(ciphertext, old_passphrase)
        rotated[key] = encrypt(plaintext, new_passphrase)

    _save_raw(store_path, rotated)
    return len(rotated)


def rotate_single(store_path: Path, variable: str, old_passphrase: str, new_passphrase: str) -> None:
    """Re-encrypt a single variable with a new passphrase."""
    data = _load_raw(store_path)

    if variable not in data:
        raise KeyError(f"Variable '{variable}' not found in store.")

    plaintext = decrypt(data[variable], old_passphrase)
    data[variable] = encrypt(plaintext, new_passphrase)
    _save_raw(store_path, data)
