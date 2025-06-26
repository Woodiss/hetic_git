
import typer
from git_scratch.utils import read_object

def ls_tree(
    oid: str = typer.Argument(..., help="OID of the tree object")
):
    """
    List the contents of a Git tree object.
    """
    try:
        obj_type, content = read_object(oid)
    except FileNotFoundError:
        typer.secho(f"Error: Object {oid} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if obj_type != "tree":
        typer.secho(f"Error: Object {oid} is not a tree.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    i = 0
    while i < len(content):
        # Mode (e.g., 100644 or 40000)
        end_mode = content.index(b' ', i)
        mode = content[i:end_mode].decode()
        i = end_mode + 1

        # Filename
        end_path = content.index(b'\x00', i)
        name = content[i:end_path].decode()
        i = end_path + 1

        # Raw SHA (20 bytes)
        oid_raw = content[i:i+20]
        oid_hex = oid_raw.hex()
        i += 20

        typer.echo(f"{mode} {oid_hex} {name}")
