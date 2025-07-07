
import typer
from git_scratch.utils.index_utils import load_index
from git_scratch.utils.tree import build_tree
from git_scratch.utils.object import write_object

def write_tree():
    """
    Writes a recursive Git tree from .git/index.json and displays its OID.
    """
    index = load_index()
    if not index:
        typer.secho("Erreur : .git/index.json not found or empty.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    tree_data = build_tree(index)
    oid = write_object(tree_data, "tree")
    typer.echo(oid)

