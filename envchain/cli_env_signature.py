"""CLI commands for env-signature feature."""
from __future__ import annotations

import click

from envchain.env_signature import (
    list_signatures,
    remove_signature,
    sign_variable,
    verify_variable,
)


def register_signature_commands(cli: click.Group, get_store) -> None:
    @cli.group("signature")
    def cmd_signature():
        """Sign and verify environment variable values."""

    @cmd_signature.command("sign")
    @click.argument("key")
    @click.argument("value")
    @click.option("--secret", required=True, envvar="ENVCHAIN_SIGN_SECRET", help="HMAC secret")
    @click.pass_context
    def cmd_sign(ctx, key, value, secret):
        """Sign VALUE for KEY and store the digest."""
        store_path = get_store(ctx)
        result = sign_variable(store_path, key, value, secret)
        if result.ok:
            click.echo(f"Signed {key!r}: {result.digest[:16]}...")
        else:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)

    @cmd_signature.command("verify")
    @click.argument("key")
    @click.argument("value")
    @click.option("--secret", required=True, envvar="ENVCHAIN_SIGN_SECRET", help="HMAC secret")
    @click.pass_context
    def cmd_verify(ctx, key, value, secret):
        """Verify VALUE against the stored digest for KEY."""
        store_path = get_store(ctx)
        result = verify_variable(store_path, key, value, secret)
        if result.ok:
            click.echo(f"OK  {key!r} signature matches.")
        else:
            click.echo(f"FAIL {key!r}: {result.error}", err=True)
            ctx.exit(1)

    @cmd_signature.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_remove(ctx, key):
        """Remove the stored signature for KEY."""
        store_path = get_store(ctx)
        removed = remove_signature(store_path, key)
        if removed:
            click.echo(f"Signature for {key!r} removed.")
        else:
            click.echo(f"No signature found for {key!r}.", err=True)

    @cmd_signature.command("list")
    @click.pass_context
    def cmd_list(ctx):
        """List all signed keys."""
        store_path = get_store(ctx)
        entries = list_signatures(store_path)
        if not entries:
            click.echo("No signatures recorded.")
            return
        for e in entries:
            click.echo(f"{e['key']:30s}  {e['digest'][:16]}...")
