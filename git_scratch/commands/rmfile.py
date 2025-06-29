
import os
import typer
from git_scratch.utils.index_utils import load_index, save_index

def rmfile(file_path: str):
    """
    Remove a file from the working directory and from the index.
    """
    index = load_index()
    filename = os.path.relpath(file_path)

    # --- Étape 1 : suppression du fichier dans le working directory ---
    if not os.path.isfile(file_path):
        typer.echo(f"File '{file_path}' does not exist in working directory.")
    else:
        try:
            os.remove(file_path)
            typer.echo(f"File '{file_path}' removed from working directory.")
        except Exception as e:
            typer.echo(f"Error while removing file: {e}")
            raise typer.Exit(code=1)

    # --- Étape 2 : suppression dans l’index ---
    new_index = [entry for entry in index if entry["path"] != filename]
    removed = len(new_index) != len(index)

    if removed:
        save_index(new_index)
        typer.echo(f"File '{filename}' removed from staging area.")
    else:
        typer.echo(f"File '{filename}' was not in the index.")

