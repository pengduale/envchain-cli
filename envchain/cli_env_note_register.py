"""Attach env-note commands to the main CLI."""
from envchain.cli_env_note import register_note_commands


def attach(cli, get_store):
    register_note_commands(cli, get_store)
