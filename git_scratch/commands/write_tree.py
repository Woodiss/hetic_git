
import typer
from git_scratch.utils.tree import create_root_tree_object

def write_tree():
    """
    Writes a recursive Git tree from .git/index.json and displays its OID.
    """
    try:
        
        oid = create_root_tree_object() 
        typer.echo(oid)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred while writing the tree: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

