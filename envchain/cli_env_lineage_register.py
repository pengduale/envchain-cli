"""Attach lineage commands to the root CLI."""

from envchain.cli_env_lineage import register_lineage_commands


def attach(cli, get_store):
    register_lineage_commands(cli, get_store)
