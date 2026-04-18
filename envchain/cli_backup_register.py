"""Helper to register backup commands into the main CLI.

Import and call `attach(cli, get_store)` from envchain/cli.py.
"""

from envchain.cli_backup import register_backup_commands


def attach(cli, get_store):
    """Attach backup sub-commands to the root CLI group."""
    register_backup_commands(cli, get_store)
