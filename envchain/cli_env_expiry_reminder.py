"""CLI commands for expiry reminders."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_expiry_reminder import get_expiry_reminders, summary


def register_expiry_reminder_commands(cli: click.Group, get_store) -> None:
    cli.add_command(cmd_reminder)


@click.group("reminder")
def cmd_reminder():
    """Expiry reminder commands."""


@cmd_reminder.command("run")
@click.option("--days", default=7, show_default=True, help="Warn if expiring within N days.")
@click.option("--no-overdue", "include_overdue", is_flag=True, default=True,
              help="Exclude already-overdue keys.")
@click.option("--summary", "show_summary", is_flag=True, default=False,
              help="Print a single summary line instead of full list.")
@click.pass_context
def cmd_reminder_run(ctx: click.Context, days: int, include_overdue: bool, show_summary: bool):
    """List keys expiring soon or already overdue."""
    store_path: Path = ctx.obj["store_path"]
    reminders = get_expiry_reminders(store_path, warn_within_days=days,
                                      include_overdue=include_overdue)

    if show_summary:
        click.echo(summary(reminders))
        return

    if not reminders:
        click.echo("No keys expiring soon.")
        return

    for r in reminders:
        tag = click.style("OVERDUE", fg="red") if r.overdue else click.style(
            f"{r.days_remaining:.1f}d", fg="yellow")
        ts = r.expires_at.strftime("%Y-%m-%d %H:%M UTC")
        click.echo(f"  {r.key:<30} {ts}  [{tag}]")
