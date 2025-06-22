
import os
import json
import typer

INDEX_PATH = os.path.join(".git", "index.json")


def ls_files():
    """
    List all staged files from the index.
    """
    if not os.path.exists(INDEX_PATH):
        typer.secho("Error: index file not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    with open(INDEX_PATH, "r") as f:
        try:
            entries = json.load(f)
        except json.JSONDecodeError:
            typer.secho("Error: index file is not valid JSON.", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    for entry in entries:
        typer.echo(entry["path"])

