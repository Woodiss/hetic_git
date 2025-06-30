import os
import typer

def resolve_ref(path):
    with open(path, "r") as f:
        content = f.read().strip()
    if content.startswith("ref: "):
        target = os.path.join(".git", content[5:])
        return resolve_ref(target)
    return content

def show_ref():
    """
    List references in a local repository
    """
    refs = {}

    # Refs dans .git/refs
    refs_dir = os.path.join(".git", "refs")
    for root, _, files in os.walk(refs_dir):
        for file in files:
            ref_path = os.path.join(root, file)
            rel_path = os.path.relpath(ref_path, ".git")
            oid = resolve_ref(ref_path)
            refs[rel_path] = oid

    # Refs dans packed-refs
    packed_refs_path = os.path.join(".git", "packed-refs")
    if os.path.exists(packed_refs_path):
        with open(packed_refs_path) as f:
            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                if " " in line:
                    oid, refname = line.strip().split(" ", 1)
                    # N’ajouter que si pas déjà présent
                    if refname not in refs:
                        refs[refname] = oid

    # Affichage trié
    for ref in sorted(refs):
        typer.echo(f"{refs[ref]} {ref}")
