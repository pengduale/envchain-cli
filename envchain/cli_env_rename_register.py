"""Attach rename commands to the main CLI."""
from envchain.cli_env_rename import register_rename_commands


def attach(cli, get_store):
    register_rename_commands(cli, get_store)
