"""CLI commands for copying variables between profiles."""
import click
from pathlib import Path

from envchain.env_copy import copy_profile_to_profile, copy_default_to_profile
from envchain.store import list_keys
from envchain.profile import list_profile_keys


def register_env_copy_commands(cli, get_store):
    @cli.group("copy")
    def cmd_copy():
        """Copy variables between profiles."""

    @cmd_copy.command("profile")
    @click.argument("src")
    @click.argument("dst")
    @click.option("--passphrase", prompt=True, hide_input=True)
    @click.option("--keys", default=None, help="Comma-separated keys to copy")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.pass_context
    def cmd_copy_profile(ctx, src, dst, passphrase, keys, overwrite):
        """Copy variables from SRC profile to DST profile."""
        store_path = get_store(ctx)
        key_list = [k.strip() for k in keys.split(",")] if keys else None
        result = copy_profile_to_profile(
            store_path, src, dst, passphrase, key_list, overwrite
        )
        click.echo(f"Copied: {len(result.copied)}, Skipped: {len(result.skipped)}, Overwritten: {len(result.overwritten)}")
        for k in result.copied:
            click.echo(f"  + {k}")
        for k in result.overwritten:
            click.echo(f"  ~ {k}")
        for k in result.skipped:
            click.echo(f"  - {k} (skipped)")

    @cmd_copy.command("to-profile")
    @click.argument("dst")
    @click.option("--passphrase", prompt=True, hide_input=True)
    @click.option("--keys", default=None, help="Comma-separated keys to copy")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.pass_context
    def cmd_copy_to_profile(ctx, dst, passphrase, keys, overwrite):
        """Copy variables from default store to DST profile."""
        store_path = get_store(ctx)
        key_list = [k.strip() for k in keys.split(",")] if keys else None
        result = copy_default_to_profile(
            store_path, dst, passphrase, key_list, overwrite
        )
        click.echo(f"Copied: {len(result.copied)}, Skipped: {len(result.skipped)}, Overwritten: {len(result.overwritten)}")
        for k in result.copied:
            click.echo(f"  + {k}")
        for k in result.overwritten:
            click.echo(f"  ~ {k}")
