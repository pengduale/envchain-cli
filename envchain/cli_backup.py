"""CLI commands for backup/restore."""

import click

from envchain.backup import create_backup, delete_backup, list_backups, restore_backup


def register_backup_commands(cli, get_store):
    @cli.group("backup")
    def cmd_backup():
        """Backup and restore the store."""

    @cmd_backup.command("create")
    @click.option("--label", default="", help="Optional label for the backup.")
    @click.pass_context
    def cmd_backup_create(ctx, label):
        """Create a backup of the current store."""
        store_path = get_store(ctx)
        path = create_backup(store_path, label=label)
        click.echo(f"Backup created: {path}")

    @cmd_backup.command("list")
    @click.pass_context
    def cmd_backup_list(ctx):
        """List all available backups."""
        store_path = get_store(ctx)
        backups = list_backups(store_path)
        if not backups:
            click.echo("No backups found.")
            return
        for b in backups:
            label = f" [{b['label']}]" if b.get("label") else ""
            status = "" if b["exists"] else " (missing archive)"
            click.echo(f"{b['created_at']}{label} -> {b['path']}{status}")

    @cmd_backup.command("restore")
    @click.argument("backup_path")
    @click.argument("target_dir")
    @click.option("--overwrite", is_flag=True, default=False)
    def cmd_backup_restore(backup_path, target_dir, overwrite):
        """Restore a backup to TARGET_DIR."""
        try:
            restore_backup(backup_path, target_dir, overwrite=overwrite)
            click.echo(f"Restored to {target_dir}")
        except FileExistsError as e:
            click.echo(f"Error: {e}", err=True)
            raise SystemExit(1)

    @cmd_backup.command("delete")
    @click.argument("backup_path")
    def cmd_backup_delete(backup_path):
        """Delete a backup archive."""
        removed = delete_backup(backup_path)
        if removed:
            click.echo(f"Deleted: {backup_path}")
        else:
            click.echo("Backup not found.", err=True)
            raise SystemExit(1)
