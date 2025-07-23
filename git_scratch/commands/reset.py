import os
from pathlib import Path
from typing import List

import typer

from git_scratch.utils.read_object import read_object
from git_scratch.utils.porcelain_commit import update_head_to_commit
from git_scratch.utils.index_utils import save_index
from git_scratch.utils.tree_walker import entries_from_tree

_HEX = set("0123456789abcdef")


def _resolve_ref(ref: str) -> str:
    """Return the full 40‑char SHA for *ref* (HEAD, branch, tag or raw SHA)."""
    # Raw SHA
    if len(ref) == 40 and all(c in _HEX for c in ref.lower()):
        return ref.lower()

    # HEAD (symbolic ou détaché)
    if ref.upper() == "HEAD":
        head_path = Path(".git") / "HEAD"
        if not head_path.is_file():
            typer.secho("Error: HEAD not found.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        head_content = head_path.read_text().strip()
        if head_content.startswith("ref: "):
            ref_path = Path(".git") / head_content[5:]
            return ref_path.read_text().strip()
        return head_content  # SHA détaché

    # Recherche dans refs/heads et refs/tags
    for cat in ("heads", "tags"):
        p = Path(".git") / "refs" / cat / ref
        if p.is_file():
            return p.read_text().strip()

    typer.secho(f"Error: unknown reference '{ref}'.", fg=typer.colors.RED)
    raise typer.Exit(code=1)


def _get_tree_oid(commit_oid: str) -> str:
    obj_type, content = read_object(commit_oid)
    if obj_type != "commit":
        typer.secho("Error: target OID is not a commit.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    first_line = content.decode(errors="replace").splitlines()[0]
    if not first_line.startswith("tree "):
        typer.secho("Error: malformed commit object.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    return first_line.split()[1]


def _checkout_tree(tree_oid: str, dest_dir: str = ".") -> None:
    """Overwrite *dest_dir* with the blobs of *tree_oid* (tracked files only)."""
    for entry in entries_from_tree(tree_oid):
        file_path = Path(dest_dir) / entry["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        _, blob_content = read_object(entry["oid"])
        with open(file_path, "wb") as f:
            f.write(blob_content)

def reset(
    ref: str = typer.Argument(..., help="Commit (SHA / ref) to reset to."),
    soft: bool = typer.Option(False, "--soft", help="Move HEAD only."),
    hard: bool = typer.Option(False, "--hard", help="Reset index and working tree."),
    mixed: bool = typer.Option(False, "--mixed", help="Reset index only."),
):
    """Re‑implémentation minimaliste de `git reset`."""
    if soft and hard:
        typer.secho("Error: choose only one of --soft / --hard.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if soft:
        mode = "soft"
    elif mixed:
        mode = "mixed"
    elif hard:
        mode = "hard"
    else:
        mode = "mixed"

    # soft
    target_oid = _resolve_ref(ref)
    update_head_to_commit(target_oid)

    # mixed
    tree_oid = _get_tree_oid(target_oid)
    if mode in {"mixed", "hard"}:
        save_index(entries_from_tree(tree_oid))

    # hard
    if mode == "hard":
        _checkout_tree(tree_oid)

    typer.echo(f"HEAD is now at {target_oid[:7]}  ({mode})")