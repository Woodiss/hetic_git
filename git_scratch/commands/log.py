
import typer
import os
from git_scratch.utils.read_object import read_object

def parse_commit(content: bytes) -> dict:
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
            # Message starts after the empty line
            commit_data["message"] = "\n".join(lines[i+1:]).strip()
            break
        i += 1

    return commit_data


def log():
    """
    Show commit logs
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

    # Affiche l'oid pour vérifier
    typer.echo(f"Starting from commit OID: {oid}")

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

        typer.secho(f"commit {oid}", fg=typer.colors.GREEN)
        typer.echo(f"Author: {commit['author']}")
        typer.echo("")
        typer.echo(f"    {commit['message']}\n")

        oid = commit["parent"]

