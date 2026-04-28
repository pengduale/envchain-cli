"""Registration shim for maturity commands."""
from .cli_env_maturity import register_maturity_commands


def attach(cli, get_store):
    register_maturity_commands(cli, get_store)
