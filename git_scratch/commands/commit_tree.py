import typer
from git_scratch.utils.commit import build_commit_object

def commit_tree(
    tree_oid: str = typer.Argument(..., help="OID of the tree object."),
    message: str = typer.Option(..., "-m", help="Commit message."),
    parent: str = typer.Option(None, "-p", help="OID of the parent commit (optional).")
):
    """
    Create a commit object pointing to a tree and optional parent commit.
    """
    try:
        oid = build_commit_object(tree_oid=tree_oid, message=message, parent_oid=parent)
        typer.echo(oid)
    except ValueError as e:
        
        typer.secho(f"Error: {e}\n\n"
                    "Please configure your user identity:\n"
                    '  git config --global user.email "you@example.com"\n'
                    '  git config --global user.name "Your Name"\n'
                    "Omit --global to set the identity only in this repository.",
                    fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)