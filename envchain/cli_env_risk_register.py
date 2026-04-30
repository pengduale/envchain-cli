"""Attach risk commands to the root CLI."""
from envchain.cli_env_risk import register_risk_commands


def attach(cli, get_store):
    register_risk_commands(cli, get_store)
