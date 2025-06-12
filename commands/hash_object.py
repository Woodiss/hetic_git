
import hashlib
import os
import zlib
import typer

app = typer.Typer()

@app.command()
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

    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()

    if write:
        obj_dir = os.path.join(".git", "objects", oid[:2])
        obj_path = os.path.join(obj_dir, oid[2:])
        os.makedirs(obj_dir, exist_ok=True)
        with open(obj_path, "wb") as f:
            f.write(zlib.compress(full_data))

    typer.echo(oid)

