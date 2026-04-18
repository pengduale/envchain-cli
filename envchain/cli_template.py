"""CLI commands for template rendering."""
from __future__ import annotations
from pathlib import Path

import click

from envchain.template import render_file, render_string, list_placeholders


def register_template_commands(cli: click.Group, get_store):
    @cli.group("template")
    def cmd_template():
        """Render templates using stored environment variables."""

    @cmd_template.command("render")
    @click.argument("template_file", type=click.Path(exists=True, path_type=Path))
    @click.option("-o", "--output", type=click.Path(path_type=Path), default=None,
                  help="Write rendered output to this file.")
    @click.pass_context
    def cmd_render(ctx, template_file: Path, output: Path):
        """Render TEMPLATE_FILE substituting {{VAR}} placeholders."""
        store_path, passphrase = get_store(ctx)
        try:
            rendered = render_file(template_file, store_path, passphrase, output)
        except KeyError as exc:
            raise click.ClickException(str(exc))
        if output:
            click.echo(f"Rendered to {output}")
        else:
            click.echo(rendered, nl=False)

    @cmd_template.command("inspect")
    @click.argument("template_file", type=click.Path(exists=True, path_type=Path))
    def cmd_inspect(template_file: Path):
        """List all {{VAR}} placeholders found in TEMPLATE_FILE."""
        text = template_file.read_text()
        placeholders = list_placeholders(text)
        if not placeholders:
            click.echo("No placeholders found.")
        else:
            for name in placeholders:
                click.echo(name)
