
import os
import typer
import hashlib
import zlib
from git_scratch.utils.index_utils import load_index, save_index, compute_mode

app = typer.Typer()

def add_file_to_index(file_path: str):
    with open(file_path, "rb") as f:
        content = f.read()

    # Prépare et compresse l’objet blob
    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()

    obj_dir = os.path.join(".git", "objects", oid[:2])
    obj_path = os.path.join(obj_dir, oid[2:])
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_path, "wb") as f:
        f.write(zlib.compress(full_data))

    # Charge et modifie l’index
    index = load_index()
    rel_path = os.path.relpath(file_path)
    mode = compute_mode(file_path)

    entry = {
        "mode": mode,
        "oid": oid,
        "path": rel_path
    }

    index = [e for e in index if e["path"] != rel_path]
    index.append(entry)

    save_index(index)
    typer.echo(f"{rel_path} added to index with OID {oid} and mode {mode}")

@app.command()
def add(file_path: str = typer.Argument(..., help="Path to file or directory to add.")):
    """
    Adds file(s) to the staging area (.git/index.json).
    """
    if not os.path.exists(file_path):
        typer.secho(f"Error: {file_path} does not exist.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if os.path.isfile(file_path):
        add_file_to_index(file_path)
    elif os.path.isdir(file_path):
        for root, _, files in os.walk(file_path):
            if ".git" in root:
                continue
            for name in files:
                full_path = os.path.join(root, name)
                if ".git" in full_path:
                    continue
                add_file_to_index(full_path)
    else:
        typer.secho("Unsupported file type.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

