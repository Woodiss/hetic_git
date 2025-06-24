import json
import os
import typer
import hashlib
import zlib
import stat

app = typer.Typer()

def compute_mode(file_path):
    st = os.stat(file_path)
    if stat.S_ISLNK(st.st_mode):
        return "120000"
    elif st.st_mode & stat.S_IXUSR:
        return "100755"
    else:
        return "100644"

def add_file_to_index(file_path: str):
    with open(file_path, "rb") as f:
        content = f.read()

    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()

    obj_dir = os.path.join(".git", "objects", oid[:2])
    obj_path = os.path.join(obj_dir, oid[2:])
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_path, "wb") as f:
        f.write(zlib.compress(full_data))

    index_path = os.path.join(".git", "index.json")
    if os.path.exists(index_path) and os.path.getsize(index_path) > 0:
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = []

    rel_path = os.path.relpath(file_path)
    mode = compute_mode(file_path)

    entry = {
        "mode": mode,
        "oid": oid,
        "path": rel_path
    }

    index = [e for e in index if e["path"] != rel_path]
    index.append(entry)

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

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
