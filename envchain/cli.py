"""Main CLI entry point for envchain."""
import click
from pathlib import Path
from envchain.store import set_variable, get_variable, delete_variable, list_keys
from envchain.cli_export import register_export_commands
from envchain.cli_rotate import register_rotate_commands
from envchain.cli_audit import register_audit_commands
from envchain.cli_profile import register_profile_commands
from envchain.cli_snapshot import register_snapshot_commands
from envchain.cli_diff import register_diff_commands
from envchain.cli_search import register_search_commands
from envchain.cli_tags import register_tag_commands
from envchain.cli_ttl import register_ttl_commands

DEFAULT_STORE = ".envchain.json"


def _get_store(ctx) -> Path:
    return Path(ctx.obj.get("store", DEFAULT_STORE))


@click.group()
@click.option("--store", default=DEFAULT_STORE, show_default=True, help="Path to store file.")
@click.pass_context
def cli(ctx, store):
    """envchain — encrypted project-level environment variable manager."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = store


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.pass_context
def cmd_set(ctx, key, value, passphrase):
    """Set an encrypted variable."""
    store_path = _get_store(ctx)
    set_variable(store_path, key, value, passphrase)
    click.echo(f"Set {key}")


@cli.command("get")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.pass_context
def cmd_get(ctx, key, passphrase):
    """Get a decrypted variable."""
    store_path = _get_store(ctx)
    value = get_variable(store_path, key, passphrase)
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.pass_context
def cmd_delete(ctx, key, passphrase):
    """Delete a variable."""
    store_path = _get_store(ctx)
    delete_variable(store_path, key, passphrase)
    click.echo(f"Deleted {key}")


@cli.command("list")
@click.pass_context
def cmd_list(ctx):
    """List all variable keys."""
    store_path = _get_store(ctx)
    keys = list_keys(store_path)
    if not keys:
        click.echo("No variables set.")
    for k in keys:
        click.echo(k)


register_export_commands(cli, _get_store)
register_rotate_commands(cli, _get_store)
register_audit_commands(cli, _get_store)
register_profile_commands(cli, _get_store)
register_snapshot_commands(cli, _get_store)
register_diff_commands(cli, _get_store)
register_search_commands(cli, _get_store)
register_tag_commands(cli, _get_store)
register_ttl_commands(cli, _get_store)
