"""CLI commands for profile management."""
import click

from envchain.cli import _get_store
from envchain.profile import (
    list_profiles,
    set_profile_variable,
    get_profile_variable,
    delete_profile_variable,
    list_profile_keys,
)


def register_profile_commands(cli: click.Group) -> None:
    cli.add_command(cmd_profile)


@click.group("profile")
def cmd_profile():
    """Manage named profiles for environment variables."""


@cmd_profile.command("list")
@click.pass_context
def cmd_list_profiles(ctx):
    """List all available profiles."""
    store_path = _get_store(ctx)
    profiles = list_profiles(store_path)
    if not profiles:
        click.echo("No profiles found.")
    else:
        for p in profiles:
            click.echo(p)


@cmd_profile.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("value")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.pass_context
def cmd_profile_set(ctx, profile, key, value, passphrase):
    """Set a variable in a named profile."""
    store_path = _get_store(ctx)
    set_profile_variable(store_path, profile, key, value, passphrase)
    click.echo(f"Set {key} in profile '{profile}'.")


@cmd_profile.command("get")
@click.argument("profile")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.pass_context
def cmd_profile_get(ctx, profile, key, passphrase):
    """Get a variable from a named profile."""
    store_path = _get_store(ctx)
    value = get_profile_variable(store_path, profile, key, passphrase)
    click.echo(value)


@cmd_profile.command("keys")
@click.argument("profile")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.pass_context
def cmd_profile_keys(ctx, profile, passphrase):
    """List keys in a named profile."""
    store_path = _get_store(ctx)
    keys = list_profile_keys(store_path, profile, passphrase)
    if not keys:
        click.echo("No variables found.")
    else:
        for k in keys:
            click.echo(k)
