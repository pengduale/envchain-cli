"""CLI commands for managing hooks."""
import click
from envchain.hooks import add_hook, remove_hook, list_hooks, HOOK_EVENTS


def register_hook_commands(cli: click.Group, get_store: callable) -> None:
    @cli.group("hook")
    def cmd_hook():
        """Manage pre/post operation hooks."""

    @cmd_hook.command("add")
    @click.argument("event", type=click.Choice(HOOK_EVENTS))
    @click.argument("command")
    @click.pass_context
    def cmd_hook_add(ctx, event, command):
        """Register a shell COMMAND to run on EVENT."""
        store_dir = get_store(ctx)
        try:
            add_hook(store_dir, event, command)
            click.echo(f"Hook added: [{event}] -> {command}")
        except ValueError as e:
            raise click.ClickException(str(e))

    @cmd_hook.command("remove")
    @click.argument("event", type=click.Choice(HOOK_EVENTS))
    @click.argument("command")
    @click.pass_context
    def cmd_hook_remove(ctx, event, command):
        """Remove a registered COMMAND from EVENT."""
        store_dir = get_store(ctx)
        removed = remove_hook(store_dir, event, command)
        if removed:
            click.echo(f"Hook removed: [{event}] -> {command}")
        else:
            raise click.ClickException(f"Hook not found for event '{event}'.")

    @cmd_hook.command("list")
    @click.option("--event", type=click.Choice(HOOK_EVENTS), default=None)
    @click.pass_context
    def cmd_hook_list(ctx, event):
        """List registered hooks, optionally filtered by EVENT."""
        store_dir = get_store(ctx)
        hooks = list_hooks(store_dir, event)
        if not any(hooks.values()):
            click.echo("No hooks registered.")
            return
        for ev, cmds in hooks.items():
            for cmd in cmds:
                click.echo(f"[{ev}] {cmd}")
