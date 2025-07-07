import os
import json
from pathlib import Path
import typer
import hashlib
import pathspec
from git_scratch.utils.index_utils import load_index, get_index_path

def git_hash_object(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    header = f"blob {len(content)}\0".encode()
    store = header + content
    return hashlib.sha1(store).hexdigest()

def list_project_files():
    # Liste tous les fichiers du projet, sauf ceux dans .git
    return [str(f) for f in Path(".").rglob("*") if f.is_file() and ".git" not in f.parts]

def load_gitignore_spec():
    # Charge le .gitignore avec pathspec
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    return pathspec.PathSpec.from_lines("gitwildmatch", [])

def status():
    import time; t0 = time.time()
    index = load_index()
    tracked_files = {item['path']: item['oid'] for item in index}
    project_files = list_project_files()
    spec = load_gitignore_spec()

    modified = []
    staged = []
    untracked = []

    for file_path in project_files:
        # On ignore les fichiers dans .gitignore
        if spec.match_file(file_path):
            continue

        if file_path in tracked_files:
            current_hash = git_hash_object(file_path)
            if current_hash == tracked_files[file_path]:
                staged.append(file_path)
            else:
                modified.append(file_path)
        else:
            untracked.append(file_path)

    if staged:
        typer.echo(typer.style("Changes to be committed:", fg=typer.colors.GREEN))
        typer.echo(typer.style("  (use \"pit reset <file>...\" to unstage)\n", fg=typer.colors.GREEN))
        for f in staged:
            typer.echo(typer.style(f"        added:   {f}", fg=typer.colors.GREEN))

    if modified:
        typer.echo(typer.style("Changes not staged for commit:", fg=typer.colors.RED))
        typer.echo(typer.style("  (use \"pit add <file>...\" to update what will be committed)", fg=typer.colors.RED))
        typer.echo(typer.style("  (use \"pit restore <file>...\" to discard changes in working directory)\n", fg=typer.colors.RED))
        for f in modified:
            typer.echo(typer.style(f"        modified:   {f}", fg=typer.colors.RED))

    if untracked:
        typer.echo(typer.style("Untracked files:", fg=typer.colors.RED))
        typer.echo(typer.style("  (use \"pit add <file>...\" to include in what will be committed)\n", fg=typer.colors.RED))
        for f in untracked:
            typer.echo(typer.style(f"        {f}", fg=typer.colors.RED))

    if not staged and not modified and not untracked:
        typer.echo("Aucun fichier modifié détecté.")
    print("Temps total:", time.time()-t0)
