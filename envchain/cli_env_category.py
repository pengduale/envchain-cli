"""CLI commands for variable category management."""
import click
from envchain.env_category import (
    set_category, get_category, remove_category,
    list_by_category, list_categories
)


def register_category_commands(cli, get_store):
    @cli.group("category")
    def cmd_category():
        """Manage variable categories."""

    @cmd_category.command("set")
    @click.argument("key")
    @click.argument("category")
    @click.pass_context
    def cmd_category_set(ctx, key, category):
        """Assign a category to a variable."""
        store_dir = get_store(ctx)
        result = set_category(store_dir, key, category)
        if result.success:
            click.echo(f"Category '{category}' assigned to '{key}'.")
        else:
            click.echo(f"Error: {result.message}", err=True)
            raise SystemExit(1)

    @cmd_category.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_category_get(ctx, key):
        """Get the category of a variable."""
        store_dir = get_store(ctx)
        cat = get_category(store_dir, key)
        if cat is None:
            click.echo(f"No category set for '{key}'.", err=True)
            raise SystemExit(1)
        click.echo(cat)

    @cmd_category.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_category_remove(ctx, key):
        """Remove the category from a variable."""
        store_dir = get_store(ctx)
        if remove_category(store_dir, key):
            click.echo(f"Category removed from '{key}'.")
        else:
            click.echo(f"No category found for '{key}'.", err=True)
            raise SystemExit(1)

    @cmd_category.command("list")
    @click.option("--group", is_flag=True, help="Group keys by category.")
    @click.pass_context
    def cmd_category_list(ctx, group):
        """List categories or keys grouped by category."""
        store_dir = get_store(ctx)
        if group:
            grouped = list_by_category(store_dir)
            if not grouped:
                click.echo("No categories defined.")
                return
            for cat in sorted(grouped):
                click.echo(f"[{cat}]")
                for k in sorted(grouped[cat]):
                    click.echo(f"  {k}")
        else:
            cats = list_categories(store_dir)
            if not cats:
                click.echo("No categories defined.")
            else:
                for c in cats:
                    click.echo(c)
