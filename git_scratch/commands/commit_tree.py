import typer
from git_scratch.utils.logique_commit_tree import build_commit_object

def commit_tree(
    tree_oid: str = typer.Argument(..., help="OID of the tree object."),
    message: str = typer.Option(..., "-m", help="Commit message."),
    parent: str = typer.Option(None, "-p", help="OID of the parent commit (optional).")
):
    """
    Create a commit object pointing to a tree and optional parent commit.
    """
    oid = build_commit_object(tree_oid=tree_oid, message=message, parent_oid=parent)
    typer.echo(oid)
