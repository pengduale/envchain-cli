"""CLI commands for variable aliasing."""
import click
from envchain.alias import set_alias, remove_alias, resolve_alias, list_aliases


def register_alias_commands(cli: click.Group, get_store) -> None:
    @cli.group("alias")
    def cmd_alias():
        """Manage variable aliases."""

    @cmd_alias.command("set")
    @click.argument("alias")
    @click.argument("key")
    @click.pass_context
    def cmd_alias_set(ctx, alias, key):
        """Create ALIAS pointing to KEY."""
        store_dir = get_store(ctx)
        set_alias(store_dir, alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' set.")

    @cmd_alias.command("remove")
    @click.argument("alias")
    @click.pass_context
    def cmd_alias_remove(ctx, alias):
        """Remove an alias."""
        store_dir = get_store(ctx)
        try:
            remove_alias(store_dir, alias)
            click.echo(f"Alias '{alias}' removed.")
        except KeyError as e:
            raise click.ClickException(str(e))

    @cmd_alias.command("get")
    @click.argument("alias")
    @click.pass_context
    def cmd_alias_get(ctx, alias):
        """Resolve ALIAS to its key."""
        store_dir = get_store(ctx)
        key = resolve_alias(store_dir, alias)
        if key is None:
            raise click.ClickException(f"Alias '{alias}' not found")
        click.echo(key)

    @cmd_alias.command("list")
    @click.pass_context
    def cmd_alias_list(ctx):
        """List all aliases."""
        store_dir = get_store(ctx)
        aliases = list_aliases(store_dir)
        if not aliases:
            click.echo("No aliases defined.")
            return
        for alias, key in sorted(aliases.items()):
            click.echo(f"{alias} -> {key}")
