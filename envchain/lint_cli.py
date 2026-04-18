import click
from envchain.lint import lint_store, LintIssue


def register_lint_commands(cli, get_store):
    @cli.group("lint")
    def cmd_lint():
        """Lint the environment variable store for issues."""

    @cmd_lint.command("run")
    @click.option("--strict", is_flag=True, help="Exit with error on warnings too.")
    @click.pass_context
    def cmd_lint_run(ctx, strict):
        """Run lint checks on the store."""
        store_path = ctx.obj["store_path"]
        passphrase = ctx.obj["passphrase"]
        issues = lint_store(store_path, passphrase)

        if not issues:
            click.echo("No issues found.")
            return

        errors = 0
        warnings = 0
        for issue in issues:
            level = issue.level.upper()
            click.echo(f"[{level}] {issue.key}: {issue.message}")
            if issue.level == "error":
                errors += 1
            else:
                warnings += 1

        click.echo(f"\n{errors} error(s), {warnings} warning(s).")

        if errors > 0 or (strict and warnings > 0):
            ctx.exit(1)
