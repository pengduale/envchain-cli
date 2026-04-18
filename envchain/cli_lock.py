"""CLI commands for store lock/unlock session management."""
import click
from envchain.lock import lock_store, unlock_store, is_locked, session_remaining


def register_lock_commands(cli, get_store):
    @cli.command("lock")
    @click.pass_context
    def cmd_lock(ctx):
        """Lock the store by clearing the active session."""
        store_path = get_store(ctx)
        lock_store(store_path)
        click.echo("Store locked.")

    @cli.command("unlock")
    @click.option("--ttl", default=300, show_default=True, help="Session TTL in seconds.")
    @click.pass_context
    def cmd_unlock(ctx, ttl):
        """Unlock the store and cache passphrase for TTL seconds."""
        store_path = get_store(ctx)
        passphrase = click.prompt("Passphrase", hide_input=True)
        unlock_store(store_path, passphrase, ttl_seconds=ttl)
        click.echo(f"Store unlocked for {ttl}s.")

    @cli.command("lock-status")
    @click.pass_context
    def cmd_lock_status(ctx):
        """Show whether the store is locked or unlocked."""
        store_path = get_store(ctx)
        if is_locked(store_path):
            click.echo("Status: locked")
        else:
            remaining = session_remaining(store_path)
            click.echo(f"Status: unlocked ({remaining:.0f}s remaining)")
