"""CLI commands for audit log inspection."""

import click
from envchain.audit import read_events, clear_log


def register_audit_commands(cli):
    cli.add_command(cmd_audit)
    cli.add_command(cmd_audit_clear)


@click.command("audit")
@click.option("--action", default=None, help="Filter by action type (set/get/delete/rotate).")
@click.option("--key", default=None, help="Filter by variable name.")
@click.pass_context
def cmd_audit(ctx, action, key):
    """Show audit log for this store."""
    store_dir = ctx.obj["store_dir"]
    events = read_events(store_dir)
    if action:
        events = [e for e in events if e.get("action") == action]
    if key:
        events = [e for e in events if e.get("key") == key]
    if not events:
        click.echo("No audit events found.")
        return
    for e in events:
        parts = [e["timestamp"], e["action"].upper(), e["key"]]
        extras = {k: v for k, v in e.items() if k not in ("timestamp", "action", "key")}
        if extras:
            parts.append(str(extras))
        click.echo("  ".join(parts))


@click.command("audit-clear")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
@click.pass_context
def cmd_audit_clear(ctx, **kwargs):
    """Clear the audit log for this store."""
    store_dir = ctx.obj["store_dir"]
    clear_log(store_dir)
    click.echo("Audit log cleared.")
