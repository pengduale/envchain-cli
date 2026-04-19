"""CLI commands for store status overview."""
from __future__ import annotations
from pathlib import Path

import click

from envchain.env_status import status_for_store


def register_status_commands(cli: click.Group, get_store):
    @cli.group("status")
    def cmd_status():
        """Show store health and key status."""

    @cmd_status.command("run")
    @click.option("--passphrase", "-p", prompt=True, hide_input=True)
    @click.option("--show-tags", is_flag=True, default=False)
    @click.pass_context
    def cmd_status_run(ctx, passphrase: str, show_tags: bool):
        """Print a status table for all keys in the store."""
        store_path = get_store(ctx)
        result = status_for_store(Path(store_path), passphrase)
        click.echo(f"Total keys : {result.total}")
        click.echo(f"Expired    : {result.expired}")
        click.echo(f"Masked     : {result.masked}")
        if result.keys:
            click.echo("")
            click.echo(f"  {'KEY':<30} {'VALUE':^8} {'EXPIRED':^8} {'MASKED':^8} {'TAGS'}")
            click.echo("  " + "-" * 70)
            for ks in result.keys:
                val_col = "yes" if ks.has_value else "no"
                exp_col = "YES" if ks.expired else "no"
                mask_col = "YES" if ks.masked else "no"
                tag_col = ",".join(ks.tags) if show_tags and ks.tags else (",".join(ks.tags) if ks.tags else "-")
                click.echo(f"  {ks.key:<30} {val_col:^8} {exp_col:^8} {mask_col:^8} {tag_col}")
        else:
            click.echo("Store is empty.")
