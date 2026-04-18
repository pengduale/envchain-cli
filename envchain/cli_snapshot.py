"""CLI commands for snapshot management."""
import click
from datetime import datetime
from envchain.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot


def register_snapshot_commands(cli, get_store):
    @cli.group("snapshot")
    def cmd_snapshot():
        """Manage store snapshots."""

    @cmd_snapshot.command("create")
    @click.option("--label", "-l", default=None, help="Optional label for the snapshot.")
    @click.pass_context
    def cmd_snapshot_create(ctx, label):
        """Create a snapshot of the current store."""
        store_path, passphrase = get_store(ctx)
        try:
            path = create_snapshot(store_path, passphrase, label)
            click.echo(f"Snapshot created: {path.name}")
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            ctx.exit(1)

    @cmd_snapshot.command("list")
    @click.pass_context
    def cmd_snapshot_list(ctx):
        """List all snapshots."""
        store_path, _ = get_store(ctx)
        snaps = list_snapshots(store_path)
        if not snaps:
            click.echo("No snapshots found.")
            return
        for s in snaps:
            dt = datetime.fromtimestamp(s["ts"]).strftime("%Y-%m-%d %H:%M:%S")
            label = f" [{s['label']}]" if s["label"] else ""
            keys = ", ".join(s["keys"])
            click.echo(f"{s['file']}{label}  {dt}  keys: {keys}")

    @cmd_snapshot.command("restore")
    @click.argument("name")
    @click.pass_context
    def cmd_snapshot_restore(ctx, name):
        """Restore a snapshot by filename."""
        store_path, passphrase = get_store(ctx)
        try:
            count = restore_snapshot(store_path, name, passphrase)
            click.echo(f"Restored {count} variable(s) from '{name}'.")
        except FileNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            ctx.exit(1)

    @cmd_snapshot.command("delete")
    @click.argument("name")
    @click.pass_context
    def cmd_snapshot_delete(ctx, name):
        """Delete a snapshot."""
        store_path, _ = get_store(ctx)
        try:
            delete_snapshot(store_path, name)
            click.echo(f"Snapshot '{name}' deleted.")
        except FileNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            ctx.exit(1)
