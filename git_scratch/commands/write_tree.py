import os
import json
import typer
import hashlib
import zlib

app = typer.Typer()

@app.command()
def write_tree():
    """
    Writes a tree object from the index and returns its OID.
    """
    index_path = "index.json"
    if not os.path.exists(index_path) or os.path.getsize(index_path) == 0:
        typer.secho("Error: the index is empty or missing.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    with open(index_path, "r") as f:
        index = json.load(f)

    entries = []

    for entry in sorted(index, key=lambda e: e["path"]):
        mode = entry["mode"]
        path = entry["path"]
        oid = bytes.fromhex(entry["oid"])

        # Format: "<mode> <path>\0<raw oid>"
        entry_line = f"{mode} {path}".encode() + b"\x00" + oid
        entries.append(entry_line)

    tree_content = b"".join(entries)

    # Prefix with "tree {size}\0"
    header = f"tree {len(tree_content)}\0".encode()
    full_data = header + tree_content

    oid = hashlib.sha1(full_data).hexdigest()

    # Save to .git/objects/
    obj_dir = os.path.join(".git", "objects", oid[:2])
    obj_path = os.path.join(obj_dir, oid[2:])
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_path, "wb") as f:
        f.write(zlib.compress(full_data))

    typer.echo(oid)
