"""CLI commands for managing variable notes."""
import click
from envchain.env_note import set_note, get_note, remove_note, list_notes


def register_note_commands(cli, get_store):
    @cli.group("note")
    def cmd_note():
        """Attach human-readable notes to variables."""

    @cmd_note.command("set")
    @click.argument("key")
    @click.argument("note")
    @click.pass_context
    def cmd_note_set(ctx, key, note):
        """Attach NOTE to KEY."""
        store_dir, _ = get_store(ctx)
        set_note(store_dir, key, note)
        click.echo(f"Note set for '{key}'.")

    @cmd_note.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_note_get(ctx, key):
        """Show the note for KEY."""
        store_dir, _ = get_store(ctx)
        note = get_note(store_dir, key)
        if note is None:
            click.echo(f"No note for '{key}'.")
            raise SystemExit(1)
        click.echo(note)

    @cmd_note.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_note_remove(ctx, key):
        """Remove the note for KEY."""
        store_dir, _ = get_store(ctx)
        removed = remove_note(store_dir, key)
        if removed:
            click.echo(f"Note removed for '{key}'.")
        else:
            click.echo(f"No note found for '{key}'.")

    @cmd_note.command("list")
    @click.pass_context
    def cmd_note_list(ctx):
        """List all keys that have notes."""
        store_dir, _ = get_store(ctx)
        notes = list_notes(store_dir)
        if not notes:
            click.echo("No notes found.")
            return
        for key, note in sorted(notes.items()):
            click.echo(f"{key}: {note}")
