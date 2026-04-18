"""CLI commands for variable tagging."""
import click
from envchain.tags import tag_variable, untag_variable, get_tags, list_by_tag, all_tags


def register_tag_commands(cli, get_store):
    @cli.group("tag")
    def cmd_tag():
        """Manage tags on environment variables."""

    @cmd_tag.command("add")
    @click.argument("key")
    @click.argument("tag")
    @click.pass_context
    def cmd_tag_add(ctx, key, tag):
        """Add TAG to variable KEY."""
        store_path = get_store(ctx)
        tag_variable(store_path, key, tag)
        click.echo(f"Tagged '{key}' with '{tag}'.")

    @cmd_tag.command("remove")
    @click.argument("key")
    @click.argument("tag")
    @click.pass_context
    def cmd_tag_remove(ctx, key, tag):
        """Remove TAG from variable KEY."""
        store_path = get_store(ctx)
        untag_variable(store_path, key, tag)
        click.echo(f"Removed tag '{tag}' from '{key}'.")

    @cmd_tag.command("list")
    @click.argument("key")
    @click.pass_context
    def cmd_tag_list(ctx, key):
        """List tags for variable KEY."""
        store_path = get_store(ctx)
        tags = get_tags(store_path, key)
        if tags:
            for t in tags:
                click.echo(t)
        else:
            click.echo(f"No tags for '{key}'.")

    @cmd_tag.command("find")
    @click.argument("tag")
    @click.pass_context
    def cmd_tag_find(ctx, tag):
        """Find all variables with TAG."""
        store_path = get_store(ctx)
        keys = list_by_tag(store_path, tag)
        if keys:
            for k in keys:
                click.echo(k)
        else:
            click.echo(f"No variables tagged '{tag}'.")

    @cmd_tag.command("all")
    @click.pass_context
    def cmd_tag_all(ctx):
        """Show all tags."""
        store_path = get_store(ctx)
        mapping = all_tags(store_path)
        if not mapping:
            click.echo("No tags defined.")
        else:
            for key, tags in mapping.items():
                click.echo(f"{key}: {', '.join(tags)}")
