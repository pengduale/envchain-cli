"""CLI commands for exporting and importing envchain variables."""

from __future__ import annotations

import sys
import click

from envchain.export import export_to_shell, export_to_dotenv, parse_dotenv


def register_export_commands(cli, get_store):
    """Attach export/import commands to the existing CLI group."""

    @cli.command("export")
    @click.option("--format", "fmt", type=click.Choice(["shell", "fish", "dotenv"]), default="shell", show_default=True)
    @click.option("--output", "-o", type=click.Path(), default=None, help="Write to file instead of stdout")
    @click.pass_context
    def cmd_export(ctx, fmt, output):
        """Export all variables to shell or dotenv format."""
        store = get_store(ctx)
        keys = store.list_keys()
        if not keys:
            click.echo("No variables stored.", err=True)
            return
        variables = {k: store.get_variable(k) for k in keys}
        if fmt == "dotenv":
            content = export_to_dotenv(variables)
        else:
            content = export_to_shell(variables, shell=fmt)
        if output:
            with open(output, "w") as fh:
                fh.write(content + "\n")
            click.echo(f"Exported {len(variables)} variable(s) to {output}")
        else:
            click.echo(content)

    @cli.command("import")
    @click.argument("dotenv_file", type=click.Path(exists=True))
    @click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
    @click.pass_context
    def cmd_import(ctx, dotenv_file, overwrite):
        """Import variables from a .env file."""
        store = get_store(ctx)
        with open(dotenv_file) as fh:
            content = fh.read()
        variables = parse_dotenv(content)
        if not variables:
            click.echo("No variables found in file.", err=True)
            sys.exit(1)
        existing = set(store.list_keys())
        imported = []
        skipped = []
        for key, value in variables.items():
            if key in existing and not overwrite:
                skipped.append(key)
                continue
            store.set_variable(key, value)
            imported.append(key)
        if imported:
            click.echo(f"Imported: {', '.join(imported)}")
        if skipped:
            click.echo(f"Skipped (already exist): {', '.join(skipped)}")
