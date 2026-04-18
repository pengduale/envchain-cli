"""CLI commands for diffing snapshots."""
from __future__ import annotations

from pathlib import Path

import click

from envchain.diff import diff_snapshots, diff_snapshot_vs_live


def register_diff_commands(cli: click.Group) -> None:
    cli.add_command(cmd_diff)


@click.group("diff")
def cmd_diff() -> None:
    """Compare snapshots or a snapshot vs the live store."""


@cmd_diff.command("snapshots")
@click.argument("snapshot_a", type=click.Path(exists=True, path_type=Path))
@click.argument("snapshot_b", type=click.Path(exists=True, path_type=Path))
@click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--show-unchanged", is_flag=True, default=False)
def cmd_diff_snapshots(
    snapshot_a: Path,
    snapshot_b: Path,
    passphrase: str,
    show_unchanged: bool,
) -> None:
    """Diff two snapshot files."""
    entries = diff_snapshots(snapshot_a, snapshot_b, passphrase)
    _print_diff(entries, show_unchanged)


@cmd_diff.command("live")
@click.argument("snapshot", type=click.Path(exists=True, path_type=Path))
@click.option("--store", "store_path", envvar="ENVCHAIN_STORE", required=True, type=click.Path(path_type=Path))
@click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--show-unchanged", is_flag=True, default=False)
def cmd_diff_live(
    snapshot: Path,
    store_path: Path,
    passphrase: str,
    show_unchanged: bool,
) -> None:
    """Diff a snapshot against the live store."""
    entries = diff_snapshot_vs_live(snapshot, store_path, passphrase)
    _print_diff(entries, show_unchanged)


def _print_diff(entries, show_unchanged: bool) -> None:
    symbols = {"added": ("+ ", "green"), "removed": ("- ", "red"), "changed": ("~ ", "yellow"), "unchanged": ("  ", None)}
    shown = 0
    for entry in entries:
        if entry.status == "unchanged" and not show_unchanged:
            continue
        sym, color = symbols[entry.status]
        if entry.status == "changed":
            click.echo(click.style(f"{sym}{entry.key}: {entry.old_value!r} -> {entry.new_value!r}", fg=color))
        elif entry.status == "added":
            click.echo(click.style(f"{sym}{entry.key}: {entry.new_value!r}", fg=color))
        elif entry.status == "removed":
            click.echo(click.style(f"{sym}{entry.key}: {entry.old_value!r}", fg=color))
        else:
            click.echo(f"{sym}{entry.key}")
        shown += 1
    if shown == 0:
        click.echo("No differences found.")
