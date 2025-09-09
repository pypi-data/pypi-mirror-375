import typer

from pylembic.validator import Validator

app = typer.Typer(
    help="pylembic CLI for validating and visualizing Alembic migrations.",
)


@app.command()
def validate(
    migrations_path: str = typer.Argument(
        default="migrations", help="Path to the migrations folder."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Show migrations validation logs."
    ),
    detect_branches: bool = typer.Option(
        False,
        "--detect-branches",
        help=(
            "Enable detection of branching migrations. "
            "If branching migrations are detected, the validation will fail."
        ),
    ),
):
    """
    Validate the migrations in the specified path.
    """
    if verbose:
        typer.echo("Verbose mode enabled.")

    if detect_branches:
        typer.echo("Detecting for branching migrations enabled.")

    typer.echo(f"Processing migrations in: {migrations_path}")
    validator = Validator(migrations_path)

    typer.echo("Validating migrations...")
    if validator.validate(detect_branches=detect_branches, verbose=verbose):
        typer.secho("Migrations validation passed!", fg=typer.colors.GREEN)
    else:
        typer.secho("Migrations validation failed!", fg=typer.colors.RED)


@app.command()
def show_graph(
    migrations_path: str = typer.Argument(
        default="migrations", help="Path to the migrations folder."
    ),
):
    """
    Visualize the migration dependency graph.
    """
    typer.echo(f"Processing migrations in: {migrations_path}")
    validator = Validator(migrations_path)

    typer.echo("Visualizing migration graph...")
    try:
        validator.show_graph()
    except ImportError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(1) from exc


if __name__ == "__main__":
    app()
