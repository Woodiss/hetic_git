import typer
import os
import time
from git_scratch.utils.read_object import read_object

def parse_commit(content: bytes) -> dict:
    """
    Parse un objet commit et retourne ses métadonnées.
    """
    lines = content.decode().split("\n")
    commit_data = {
        "tree": None,
        "parent": None,
        "author": None,
        "committer": None,
        "message": ""
    }

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("tree "):
            commit_data["tree"] = line.split(" ")[1]
        elif line.startswith("parent "):
            commit_data["parent"] = line.split(" ")[1]
        elif line.startswith("author "):
            commit_data["author"] = line[7:]
        elif line.startswith("committer "):
            commit_data["committer"] = line[10:]
        elif line == "":
            # Le message commence après la ligne vide
            commit_data["message"] = "\n".join(lines[i+1:]).strip()
            break
        i += 1

    return commit_data


def format_git_date(timestamp: str, tz_offset: str) -> str:
    """
    Convertit un timestamp UNIX + offset en format git log.
    """
    t = time.localtime(int(timestamp))
    # Format identique à `git log`
    return time.strftime("%a %b %d %H:%M:%S %Y", t) + f" {tz_offset}"


def log():
    """
    Réimplémente `git log` en lisant les commits dans .git/objects.
    """
    try:
        head_path = os.path.join(".git", "HEAD")
        with open(head_path) as f:
            head_ref = f.read().strip()
    except FileNotFoundError:
        typer.secho(f"File not found: {head_path}", fg=typer.colors.RED)
        return

    if head_ref.startswith("ref:"):
        ref_path = os.path.join(".git", head_ref[5:])
        try:
            with open(ref_path) as f:
                oid = f.read().strip()
        except FileNotFoundError:
            typer.secho(f"File not found: {ref_path}", fg=typer.colors.RED)
            return
    else:
        oid = head_ref

    if not oid:
        typer.secho("No commits found or repository not initialized.", fg=typer.colors.RED)
        return

    while oid:
        try:
            obj_type, content = read_object(oid)
        except FileNotFoundError:
            typer.secho(f"Object {oid} not found in .git/objects", fg=typer.colors.RED)
            return

        if obj_type != "commit":
            typer.secho(f"Expected commit, got {obj_type}", fg=typer.colors.RED)
            return

        commit = parse_commit(content)

        # Récupère l'auteur + timestamp
        author_parts = commit["author"].rsplit(" ", 2)
        author_name = author_parts[0]
        timestamp = author_parts[1]
        tz_offset = author_parts[2]

        date_str = format_git_date(timestamp, tz_offset)

        # Format identique à git log
        typer.echo(f"commit {oid}")
        typer.echo(f"Author: {author_name}")
        typer.echo(f"Date:   {date_str}\n")
        typer.echo(f"    {commit['message']}\n")

        oid = commit["parent"]
