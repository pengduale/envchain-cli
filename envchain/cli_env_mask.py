"""CLI commands for masking/unmasking variables."""
import click
from envchain.env_mask import mask_variable, unmask_variable, is_masked, list_masked


def register_mask_commands(cli, get_store):
    @cli.group("mask")
    def cmd_mask():
        """Manage variable masking (hide values in output)."""

    @cmd_mask.command("set")
    @click.argument("key")
    @click.pass_context
    def cmd_mask_set(ctx, key):
        """Mask a variable so its value is hidden in output."""
        store_dir, _ = get_store(ctx)
        result = mask_variable(store_dir, key)
        click.echo(f"Masked: {result.key}")

    @cmd_mask.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_mask_remove(ctx, key):
        """Unmask a variable."""
        store_dir, _ = get_store(ctx)
        result = unmask_variable(store_dir, key)
        click.echo(f"Unmasked: {result.key}")

    @cmd_mask.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_mask_get(ctx, key):
        """Check if a variable is masked."""
        store_dir, _ = get_store(ctx)
        masked = is_masked(store_dir, key)
        click.echo("masked" if masked else "not masked")

    @cmd_mask.command("list")
    @click.pass_context
    def cmd_mask_list(ctx):
        """List all masked variables."""
        store_dir, _ = get_store(ctx)
        keys = list_masked(store_dir)
        if not keys:
            click.echo("No masked variables.")
        else:
            for k in keys:
                click.echo(k)
