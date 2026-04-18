"""CLI commands for TTL management."""
import time
import click
from pathlib import Path
from envchain.ttl import set_ttl, clear_ttl, get_expiry, purge_expired
from envchain.store import delete_variable


def register_ttl_commands(cli, get_store):
    @cli.group("ttl")
    def cmd_ttl():
        """Manage variable expiry (TTL)."""

    @cmd_ttl.command("set")
    @click.argument("key")
    @click.argument("seconds", type=int)
    @click.pass_context
    def cmd_ttl_set(ctx, key, seconds):
        """Set TTL for KEY to SECONDS from now."""
        store_path = get_store(ctx)
        set_ttl(store_path, key, seconds)
        expiry = time.time() + seconds
        click.echo(f"TTL set: {key} expires at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry))}")

    @cmd_ttl.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_ttl_get(ctx, key):
        """Show remaining TTL for KEY."""
        store_path = get_store(ctx)
        expiry = get_expiry(store_path, key)
        if expiry is None:
            click.echo(f"{key}: no TTL set")
        else:
            remaining = expiry - time.time()
            if remaining <= 0:
                click.echo(f"{key}: expired")
            else:
                click.echo(f"{key}: {int(remaining)}s remaining")

    @cmd_ttl.command("clear")
    @click.argument("key")
    @click.pass_context
    def cmd_ttl_clear(ctx, key):
        """Remove TTL for KEY."""
        store_path = get_store(ctx)
        clear_ttl(store_path, key)
        click.echo(f"TTL cleared for {key}")

    @cmd_ttl.command("purge")
    @click.option("--passphrase", prompt=True, hide_input=True)
    @click.pass_context
    def cmd_ttl_purge(ctx, passphrase):
        """Delete all expired variables from the store."""
        store_path = get_store(ctx)
        expired = purge_expired(store_path)
        if not expired:
            click.echo("No expired variables.")
            return
        for key in expired:
            try:
                delete_variable(store_path, key, passphrase)
            except Exception:
                pass
        click.echo(f"Purged {len(expired)} expired variable(s): {', '.join(expired)}")
