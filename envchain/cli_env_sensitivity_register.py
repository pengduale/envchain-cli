"""Attach sensitivity commands to the main CLI."""

from envchain.cli_env_sensitivity import register_sensitivity_commands


def attach(cli, get_store):
    register_sensitivity_commands(cli, get_store)
