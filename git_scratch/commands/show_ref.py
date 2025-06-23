
import os
import typer

def show_ref():
    """
    List all references and their OIDs.
    """
    refs_dir = os.path.join(".git", "refs")

    if not os.path.isdir(refs_dir):
        typer.secho("Error: .git/refs directory not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    for root, _, files in os.walk(refs_dir):
        for file in files:
            ref_path = os.path.join(root, file)
            with open(ref_path, "r") as f:
                oid = f.read().strip()
            # Get relative path from .git (e.g., refs/heads/main)
            rel_path = os.path.relpath(ref_path, os.path.join(".git"))
            typer.echo(f"{oid} {rel_path}")

    # Optionally: read packed-refs
    packed_refs = os.path.join(".git", "packed-refs")
    if os.path.exists(packed_refs):
        with open(packed_refs) as f:
            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                if " " in line:
                    oid, ref = line.strip().split(" ")
                    typer.echo(f"{oid} {ref}")
