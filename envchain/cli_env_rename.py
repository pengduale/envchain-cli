"""CLI commands for renaming environment variable keys."""
import click
from envchain.env_rename import rename_variable, rename_all_profiles
from envchain.profile import list_profiles


def register_rename_commands(cli, get_store):
    @cli.group("rename")
    def cmd_rename():
        """Rename environment variable keys."""

    @cmd_rename.command("run")
    @click.argument("old_key")
    @click.argument("new_key")
    @click.option("--profile", default=None, help="Profile name (default: default store)")
    @click.option("--overwrite", is_flag=True, default=False, help="Overwrite destination if exists")
    @click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
    def cmd_rename_run(old_key, new_key, profile, overwrite, passphrase):
        """Rename OLD_KEY to NEW_KEY."""
        store_path = get_store()
        result = rename_variable(store_path, old_key, new_key, passphrase,
                                 profile=profile, overwrite=overwrite)
        if result.success:
            click.echo(f"Renamed {old_key} -> {new_key}" + (f" in profile [{profile}]" if profile else ""))
        else:
            click.echo(f"Skipped: {result.reason}", err=True)
            raise SystemExit(1)

    @cmd_rename.command("all-profiles")
    @click.argument("old_key")
    @click.argument("new_key")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
    def cmd_rename_all(old_key, new_key, overwrite, passphrase):
        """Rename OLD_KEY to NEW_KEY across all profiles."""
        store_path = get_store()
        profiles = list_profiles(store_path)
        if not profiles:
            click.echo("No profiles found.")
            return
        results = rename_all_profiles(store_path, old_key, new_key, passphrase,
                                      profiles, overwrite=overwrite)
        for r in results:
            status = "ok" if r.success else f"skip: {r.reason}"
            click.echo(f"  [{r.profile}] {r.old_key} -> {r.new_key}: {status}")
