"""CLI commands for syncing variables between profiles."""
import click
from pathlib import Path
from envchain.env_sync import sync_profiles, sync_profile_to_default


def register_sync_commands(cli, get_store):
    @cli.group("sync")
    def cmd_sync():
        """Sync variables between profiles."""

    @cmd_sync.command("profiles")
    @click.argument("src")
    @click.argument("dst")
    @click.option("--passphrase", prompt=True, hide_input=True)
    @click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
    def cmd_sync_profiles(src, dst, passphrase, overwrite):
        """Sync all variables from SRC profile to DST profile."""
        store_path = get_store()
        result = sync_profiles(Path(store_path), src, dst, passphrase, overwrite=overwrite)
        click.echo(f"Copied:      {len(result.copied)} key(s)")
        click.echo(f"Overwritten: {len(result.overwritten)} key(s)")
        click.echo(f"Skipped:     {len(result.skipped)} key(s)")
        for k in result.copied:
            click.echo(f"  + {k}")
        for k in result.overwritten:
            click.echo(f"  ~ {k}")
        for k in result.skipped:
            click.echo(f"  - {k} (skipped)")

    @cmd_sync.command("to-default")
    @click.argument("src")
    @click.option("--passphrase", prompt=True, hide_input=True)
    @click.option("--overwrite", is_flag=True, default=False)
    def cmd_sync_to_default(src, passphrase, overwrite):
        """Sync variables from SRC profile into the default store."""
        store_path = get_store()
        result = sync_profile_to_default(Path(store_path), src, passphrase, overwrite=overwrite)
        click.echo(f"Copied:      {len(result.copied)} key(s)")
        click.echo(f"Overwritten: {len(result.overwritten)} key(s)")
        click.echo(f"Skipped:     {len(result.skipped)} key(s)")
