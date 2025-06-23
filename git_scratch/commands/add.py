import json
import os
import typer
import hashlib
import zlib

def add(file_path: str = typer.Argument(..., help="Path to the file to stage.")):
    """
    Adds a file to the staging area (.git/index.json).
    """
    if not os.path.isfile(file_path):
        typer.secho(f"Error: {file_path} is not a valid file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Read the file content
    with open(file_path, "rb") as f:
        content = f.read()

    # Create the blob object
    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()

    # Save to .git/objects/
    obj_dir = os.path.join(".git", "objects", oid[:2])
    obj_path = os.path.join(obj_dir, oid[2:])
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_path, "wb") as f:
        f.write(zlib.compress(full_data))

    # Load or create .git/index.json
    index_path = os.path.join(".git", "index.json")
    if os.path.exists(index_path) and os.path.getsize(index_path) > 0:
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = []

    # Use relative path (optional, depends où tu exécutes)
    rel_path = os.path.relpath(file_path)

    # Create the entry with mode, oid, and path
    entry = {
        "mode": "100644",  # standard mode for a normal file
        "oid": oid,
        "path": rel_path
    }

    # Remove any existing entry with the same path
    index = [e for e in index if e["path"] != rel_path]

    # Add the new entry
    index.append(entry)

    # Write to .git/index.json
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

    typer.echo(f"{rel_path} added to index with OID {oid}")
