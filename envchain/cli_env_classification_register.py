"""Attach classification commands to the main CLI."""

from envchain.cli_env_classification import register_classification_commands


def attach(cli, get_store):
    register_classification_commands(cli, get_store)
