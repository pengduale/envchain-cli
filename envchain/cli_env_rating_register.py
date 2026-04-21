"""Thin registration shim so the main CLI can attach rating commands."""

from envchain.cli_env_rating import register_rating_commands


def attach(cli, get_store) -> None:
    """Register rating commands onto *cli*."""
    register_rating_commands(cli, get_store)
