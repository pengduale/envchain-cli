"""CLI commands for managing boolean flags on environment variables."""

from __future__ import annotations

import click
from envchain.env_flag import set_flag, get_flag, get_all_flags, remove_flag, list_flagged, VALID_FLAGS


def register_flag_commands(cli, get_store):
    @cli.group("flag")
    def cmd_flag():
        """Manage boolean flags on variables (required, sensitive, readonly, deprecated)."""

    @cmd_flag.command("set")
    @click.argument("key")
    @click.argument("flag", type=click.Choice(sorted(VALID_FLAGS)))
    @click.option("--off", is_flag=True, help="Set flag to False instead of True.")
    @click.pass_context
    def cmd_flag_set(ctx, key, flag, off):
        """Set a flag on a variable."""
        store_path = get_store(ctx)
        result = set_flag(store_path, key, flag, value=not off)
        state = "off" if off else "on"
        click.echo(f"Flag '{flag}' set to {state} for '{key}'.")

    @cmd_flag.command("get")
    @click.argument("key")
    @click.argument("flag", type=click.Choice(sorted(VALID_FLAGS)))
    @click.pass_context
    def cmd_flag_get(ctx, key, flag):
        """Get the value of a flag on a variable."""
        store_path = get_store(ctx)
        value = get_flag(store_path, key, flag)
        if value is None:
            click.echo(f"Flag '{flag}' not set for '{key}'.")
        else:
            click.echo(f"{flag}={value}")

    @cmd_flag.command("remove")
    @click.argument("key")
    @click.argument("flag", type=click.Choice(sorted(VALID_FLAGS)))
    @click.pass_context
    def cmd_flag_remove(ctx, key, flag):
        """Remove a flag from a variable."""
        store_path = get_store(ctx)
        removed = remove_flag(store_path, key, flag)
        if removed:
            click.echo(f"Flag '{flag}' removed from '{key}'.")
        else:
            click.echo(f"Flag '{flag}' was not set for '{key}'.")

    @cmd_flag.command("list")
    @click.argument("key")
    @click.pass_context
    def cmd_flag_list(ctx, key):
        """List all flags set on a variable."""
        store_path = get_store(ctx)
        flags = get_all_flags(store_path, key)
        if not flags:
            click.echo(f"No flags set for '{key}'.")
        else:
            for f, v in sorted(flags.items()):
                click.echo(f"  {f}: {v}")

    @cmd_flag.command("search")
    @click.argument("flag", type=click.Choice(sorted(VALID_FLAGS)))
    @click.pass_context
    def cmd_flag_search(ctx, flag):
        """List all variables with a given flag set to True."""
        store_path = get_store(ctx)
        keys = list_flagged(store_path, flag)
        if not keys:
            click.echo(f"No variables with '{flag}' flag.")
        else:
            for k in sorted(keys):
                click.echo(f"  {k}")
