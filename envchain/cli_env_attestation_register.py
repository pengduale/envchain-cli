"""Attach attestation commands to the root CLI."""
from .cli_env_attestation import register_attestation_commands


def attach(cli, get_store):
    register_attestation_commands(cli, get_store)
