import os
import json
from pathlib import Path
import typer

def get_index_path():
    """
    Returns the path to the .git/index.json file dynamically,
    based on the current working directory.
    """
    return Path(os.getcwd()) / ".git" / "index.json"

def load_index():
    """
    Load the index.json file from .git/ and return its content.
    If the file does not exist, return an empty list.
    """
    index_path = get_index_path()
    if not index_path.exists():
        return []

    with open(index_path, "r") as f:
        return json.load(f)

def save_index(index):
    """
    Save the given index to .git/index.json.
    """
    index_path = get_index_path()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

def rmfile(file_path: str):
    """
    Remove a file from the working directory and from the index.
    """
    index = load_index()
    filename = os.path.basename(file_path)

    # --- Step 1: Remove the file from the working directory ---
    if not os.path.isfile(file_path):
        typer.echo(f"File '{file_path}' does not exist in working directory.")
    else:
        try:
            os.remove(file_path)
            typer.echo(f"File '{file_path}' removed from working directory.")
        except Exception as e:
            typer.echo(f"Error while removing file: {e}")
            raise typer.Exit(code=1)

    # --- Step 2: Remove from index ---
    new_index = []
    removed = False
    for entry in index:
        if entry["path"] == filename:
            removed = True
        else:
            new_index.append(entry)

    if removed:
        save_index(new_index)
        typer.echo(f"File '{filename}' removed from staging area.")
    else:
        typer.echo(f"File '{filename}' was not in the index.")
