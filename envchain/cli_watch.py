"""CLI commands for watching a store for live changes."""
from __future__ import annotations
import click
from pathlib import Path
from envchain.watch import watch_store, diff_on_change


def register_watch_commands(cli: click.Group, get_store) -> None:
    @cli.group("watch")
    def cmd_watch():
        """Watch store for changes."""

    @cmd_watch.command("start")
    @click.option("--interval", default=1.0, show_default=True, help="Poll interval in seconds.")
    @click.option("--passphrase", prompt=True, hide_input=True)
    @click.pass_context
    def cmd_watch_start(ctx, interval: float, passphrase: str):
        """Watch the store and print key changes as they happen."""
        store_path = get_store(ctx)
        click.echo(f"Watching {store_path} every {interval}s … (Ctrl+C to stop)")
        cb = diff_on_change(Path(store_path), passphrase)
        try:
            watch_store(Path(store_path), cb, interval=interval)
        except KeyboardInterrupt:
            click.echo("\nStopped.")
