"""Main CLI entry point for envchain."""

import os
import click
from envchain.store import set_variable, get_variable, delete_variable, list_keys
from envchain.cli_export import register_export_commands
from envchain.cli_rotate import register_rotate_commands
from envchain.cli_audit import register_audit_commands
from envchain.audit import log_event


def _get_store(ctx):
    store_path = os.environ.get("ENVCHAIN_STORE", ".envchain.json")
    passphrase = os.environ.get("ENVCHAIN_PASSPHRASE", "")
    store_dir = os.path.dirname(os.path.abspath(store_path))
    ctx.ensure_object(dict)
    ctx.obj["store_path"] = store_path
    ctx.obj["passphrase"] = passphrase
    ctx.obj["store_dir"] = store_dir


@click.group()
@click.pass_context
def cli(ctx):
    """envchain — encrypted project environment variable manager."""
    _get_store(ctx)


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def cmd_set(ctx, key, value):
    """Set an encrypted environment variable."""
    store_path = ctx.obj["store_path"]
    passphrase = ctx.obj["passphrase"]
    store_dir = ctx.obj["store_dir"]
    set_variable(store_path, passphrase, key, value)
    log_event(store_dir, "set", key)
    click.echo(f"Set {key}")


@cli.command("get")
@click.argument("key")
@click.pass_context
def cmd_get(ctx, key):
    """Get a decrypted environment variable."""
    store_path = ctx.obj["store_path"]
    passphrase = ctx.obj["passphrase"]
    store_dir = ctx.obj["store_dir"]
    value = get_variable(store_path, passphrase, key)
    log_event(store_dir, "get", key)
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.pass_context
def cmd_delete(ctx, key):
    """Delete an environment variable."""
    store_path = ctx.obj["store_path"]
    passphrase = ctx.obj["passphrase"]
    store_dir = ctx.obj["store_dir"]
    delete_variable(store_path, key)
    log_event(store_dir, "delete", key)
    click.echo(f"Deleted {key}")


@cli.command("list")
@click.pass_context
def cmd_list(ctx):
    """List all variable keys."""
    store_path = ctx.obj["store_path"]
    keys = list_keys(store_path)
    if not keys:
        click.echo("No variables set.")
    for k in keys:
        click.echo(k)


register_export_commands(cli)
register_rotate_commands(cli)
register_audit_commands(cli)
