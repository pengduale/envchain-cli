"""Run a subprocess with decrypted environment variables injected."""
import os
import subprocess
from typing import Optional

from envchain.store import list_keys, get_variable
from envchain.profile import get_profile_variable, list_profiles


def build_env(
    store_path: str,
    passphrase: str,
    profile: Optional[str] = None,
    extra: Optional[dict] = None,
) -> dict:
    """Return os.environ copy augmented with decrypted variables."""
    env = os.environ.copy()

    if profile is None:
        keys = list_keys(store_path)
        for key in keys:
            value = get_variable(store_path, key, passphrase)
            if value is not None:
                env[key] = value
    else:
        from envchain.profile import _profile_store_path, list_profile_keys
        profile_path = _profile_store_path(store_path, profile)
        keys = list_profile_keys(store_path, profile)
        for key in keys:
            value = get_profile_variable(store_path, profile, key, passphrase)
            if value is not None:
                env[key] = value

    if extra:
        env.update(extra)

    return env


def run_command(
    command: list,
    store_path: str,
    passphrase: str,
    profile: Optional[str] = None,
    extra: Optional[dict] = None,
) -> int:
    """Execute *command* with injected env vars. Returns exit code."""
    env = build_env(store_path, passphrase, profile=profile, extra=extra)
    result = subprocess.run(command, env=env)
    return result.returncode
