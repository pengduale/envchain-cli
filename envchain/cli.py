"""CLI entry point for envchain."""

import getpass
import sys
from pathlib import Path

import click

from envchain.store import (
    set_variable,
    get_variable,
    delete_variable,
    list_keys,
    DEFAULT_STORE_FILE,
)


def _get_store(ctx: click.Context) -> Path:
    return Path(ctx.obj.get("store", DEFAULT_STORE_FILE))


@click.group()
@click.option("--store", default=DEFAULT_STORE_FILE, show_default=True, help="Path to the store file.")
@click.pass_context
def cli(ctx: click.Context, store: str) -> None:
    """envchain — encrypted project-level environment variable manager."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = store


@cli.command("set")
@click.argument("key")
@click.argument("value", required=False)
@click.pass_context
def cmd_set(ctx: click.Context, key: str, value: str) -> None:
    """Set (encrypt and store) an environment variable."""
    if value is None:
        value = click.prompt(f"Value for {key}", hide_input=True)
    passphrase = getpass.getpass("Passphrase: ")
    set_variable(key, value, passphrase, _get_store(ctx))
    click.echo(f"✔ '{key}' stored.")


@cli.command("get")
@click.argument("key")
@click.pass_context
def cmd_get(ctx: click.Context, key: str) -> None:
    """Decrypt and print an environment variable."""
    passphrase = getpass.getpass("Passphrase: ")
    try:
        click.echo(get_variable(key, passphrase, _get_store(ctx)))
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("key")
@click.pass_context
def cmd_delete(ctx: click.Context, key: str) -> None:
    """Remove a variable from the store."""
    try:
        delete_variable(key, _get_store(ctx))
        click.echo(f"✔ '{key}' deleted.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cli.command("list")
@click.pass_context
def cmd_list(ctx: click.Context) -> None:
    """List all stored variable names."""
    keys = list_keys(_get_store(ctx))
    if not keys:
        click.echo("No variables stored.")
    else:
        click.echo("\n".join(keys))
