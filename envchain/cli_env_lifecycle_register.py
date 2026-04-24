"""Registration shim for lifecycle CLI commands."""

from envchain.cli_env_lifecycle import register_lifecycle_commands


def attach(cli, get_store):
    register_lifecycle_commands(cli, get_store)
