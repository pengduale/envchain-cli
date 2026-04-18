"""Import environment variables from the current process environment."""
from __future__ import annotations

import os
import re
from typing import List, Tuple


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')


def _is_valid_key(key: str) -> bool:
    return bool(_VALID_KEY_RE.match(key))


def import_from_env(
    store_path: str,
    passphrase: str,
    prefix: str | None = None,
    keys: List[str] | None = None,
    strip_prefix: bool = False,
) -> List[Tuple[str, str]]:
    """Import variables from os.environ into the store.

    Args:
        store_path: Path to the envchain store file.
        passphrase: Encryption passphrase.
        prefix: Only import variables whose names start with this prefix.
        keys: Explicit list of variable names to import.
        strip_prefix: If True and prefix is set, strip the prefix from stored key names.

    Returns:
        List of (key, stored_as) tuples for imported variables.
    """
    from envchain.store import set_variable

    candidates: dict[str, str] = {}

    if keys:
        for k in keys:
            if k in os.environ:
                candidates[k] = os.environ[k]
    elif prefix:
        for k, v in os.environ.items():
            if k.startswith(prefix):
                candidates[k] = v
    else:
        for k, v in os.environ.items():
            if _is_valid_key(k):
                candidates[k] = v

    imported: List[Tuple[str, str]] = []
    for k, v in candidates.items():
        stored_as = k
        if strip_prefix and prefix and k.startswith(prefix):
            stored_as = k[len(prefix):]
        if not stored_as:
            continue
        set_variable(store_path, passphrase, stored_as, v)
        imported.append((k, stored_as))

    return imported


def list_importable(prefix: str | None = None) -> List[str]:
    """Return env var names that would be imported given the prefix filter."""
    if prefix:
        return [k for k in os.environ if k.startswith(prefix)]
    return [k for k in os.environ if _is_valid_key(k)]
