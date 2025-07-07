import os
import typer
from git_scratch.utils.object import write_object
from git_scratch.utils.hash import compute_blob_hash


def hash_object(
    file_path: str = typer.Argument(..., help="Path to the file to hash."),
    write: bool = typer.Option(False, "--write", "-w", help="Store object in .git/objects.")
):
    """
    Computes SHA-1 hash of a file's contents and optionally writes it as a Git blob.
    """
    if not os.path.isfile(file_path):
        typer.secho(f"Error: {file_path} is not a valid file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    with open(file_path, 'rb') as f:
        content = f.read()
        
    oid, _ = compute_blob_hash(content)
    if write:
        write_object(content, "blob")

    typer.echo(oid)
