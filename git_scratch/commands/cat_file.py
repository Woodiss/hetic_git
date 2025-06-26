
import typer
from git_scratch.utils import read_object  # Assure-toi que le chemin est correct

def cat_file(
    oid: str = typer.Argument(..., help="SHA-1 object ID to inspect."),
    type: bool = typer.Option(False, "-t", help="Show the type of the object."),
    pretty: bool = typer.Option(False, "-p", help="Pretty-print the object’s content.")
):
    """
    Show information about a Git object by its OID.
    """
    if not (type or pretty):
        typer.secho("Error: You must specify either -t or -p.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if len(oid) != 40 or not all(c in "0123456789abcdef" for c in oid.lower()):
        typer.secho(f"Error: Invalid OID format: {oid}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    try:
        obj_type, content = read_object(oid)
    except FileNotFoundError:
        typer.secho(f"Error: Object {oid} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception:
        typer.secho("Error: Failed to read Git object.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if type:
        typer.echo(obj_type)
    elif pretty:
        if obj_type != "blob":
            typer.secho(f"Error: Pretty-print not supported for object type '{obj_type}'.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        typer.echo(content.decode(errors="replace"))

