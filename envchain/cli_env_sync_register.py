"""Attach env_sync commands to the main CLI."""
from envchain.cli_env_sync import register_sync_commands


def attach(cli, get_store):
    register_sync_commands(cli, get_store)
