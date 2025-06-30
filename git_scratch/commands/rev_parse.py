import os
import re
import pathlib
import typer


def rev_parse(
    ref: str = typer.Argument(..., help="Reference to resolve (branch, tag, SHA, HEAD)"),
):
    """Resolve *ref* to its full 40‑character SHA‑1 and print it.

    Handles:
    1. Full SHA (40 hex)
    2. Abbreviated SHA (4‑39 hex)
    3. refs/heads/<name> and refs/tags/<name>
    4. HEAD (symbolic or detached)
    5. packed‑refs lookup
    """
    # check if current directory has a Git repository
    git_dir = pathlib.Path(".git")
    if not git_dir.is_dir():
        typer.secho("Error: .git directory not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # regex for check if a string is a valid hexadecimal
    HEX_RE = re.compile(r"^[0-9a-fA-F]+$")

    # check if an object exists
    def object_exists(sha: str) -> bool:
        return (git_dir / "objects" / sha[:2] / sha[2:]).is_file()

    # full SHA
    if len(ref) == 40 and HEX_RE.fullmatch(ref):
        if object_exists(ref):
            typer.echo(ref.lower())
            return
        typer.secho(f"Error: unknown revision '{ref}'", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # abbreviated SHA
    if 4 <= len(ref) < 40 and HEX_RE.fullmatch(ref):
        matches = []
        obj_base = git_dir / "objects"
        for sub in obj_base.iterdir():
            if sub.is_dir() and len(sub.name) == 2 and sub.name not in ("info", "pack"):
                for obj in sub.iterdir():
                    if obj.is_file():
                        sha = sub.name + obj.name
                        if sha.startswith(ref.lower()):
                            matches.append(sha)
        if len(matches) == 1:
            typer.echo(matches[0])
            return
        if len(matches) > 1:
            typer.secho(f"Error: ambiguous revision '{ref}'", fg=typer.colors.RED)
        else:
            typer.secho(f"Error: unknown revision '{ref}'", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # refs/heads or refs/tags (branches or tags)
    for subdir in ("refs/heads", "refs/tags"):
        path = git_dir / subdir / ref
        if path.is_file():
            sha = path.read_text().strip()
            if sha:
                typer.echo(sha.lower())
                return

    # HEAD
    if ref.upper() == "HEAD":
        head_path = git_dir / "HEAD"
        if head_path.is_file():
            content = head_path.read_text().strip()
            if content.startswith("ref:"):
                target = git_dir / content[5:].strip()
                if target.is_file():
                    typer.echo(target.read_text().strip().lower())
                    return
            elif len(content) == 40 and HEX_RE.fullmatch(content):
                typer.echo(content.lower())
                return
        typer.secho("Error: HEAD not found or invalid.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # packed‑refs
    packed = git_dir / "packed-refs"
    if packed.is_file():
        with packed.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                sha, refname = line.split(" ", 1)
                if refname in (f"refs/heads/{ref}", f"refs/tags/{ref}"):
                    typer.echo(sha.lower())
                    return

    typer.secho(f"Error: unknown revision '{ref}'", fg=typer.colors.RED)
    raise typer.Exit(code=1)