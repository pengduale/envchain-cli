"""CLI commands for variable pinning."""
import click
from pathlib import Path
from envchain.env_pin import pin_variable, unpin_variable, get_pin, list_pins


def register_pin_commands(cli: click.Group, get_store):
    @cli.group("pin")
    def cmd_pin():
        """Pin variables to snapshot versions."""

    @cmd_pin.command("set")
    @click.argument("key")
    @click.argument("snapshot_id")
    @click.option("--profile", default="default", show_default=True)
    @click.pass_context
    def cmd_pin_set(ctx, key, snapshot_id, profile):
        """Pin KEY to SNAPSHOT_ID."""
        store_path = Path(get_store(ctx))
        result = pin_variable(store_path, key, snapshot_id, profile)
        if result.success:
            click.echo(f"Pinned {key} -> {snapshot_id} (profile: {profile})")
        else:
            click.echo(f"Error: {result.message}", err=True)
            ctx.exit(1)

    @cmd_pin.command("remove")
    @click.argument("key")
    @click.option("--profile", default="default", show_default=True)
    @click.pass_context
    def cmd_pin_remove(ctx, key, profile):
        """Remove pin for KEY."""
        store_path = Path(get_store(ctx))
        result = unpin_variable(store_path, key, profile)
        if result.success:
            click.echo(f"Unpinned {key} (was -> {result.snapshot_id})")
        else:
            click.echo(f"Error: {result.message}", err=True)
            ctx.exit(1)

    @cmd_pin.command("get")
    @click.argument("key")
    @click.option("--profile", default="default", show_default=True)
    @click.pass_context
    def cmd_pin_get(ctx, key, profile):
        """Show snapshot pinned to KEY."""
        store_path = Path(get_store(ctx))
        snap = get_pin(store_path, key, profile)
        if snap is None:
            click.echo(f"{key} is not pinned")
        else:
            click.echo(snap)

    @cmd_pin.command("list")
    @click.option("--profile", default="default", show_default=True)
    @click.pass_context
    def cmd_pin_list(ctx, profile):
        """List all pins for a profile."""
        store_path = Path(get_store(ctx))
        pins = list_pins(store_path, profile)
        if not pins:
            click.echo("No pins set.")
        else:
            for key, snap in sorted(pins.items()):
                click.echo(f"{key} -> {snap}")
