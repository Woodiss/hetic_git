import os
import zlib
import typer

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

    obj_path = os.path.join(".git", "objects", oid[:2], oid[2:])
    if not os.path.exists(obj_path):
        typer.secho(f"Error: Object {oid} not found in .git/objects.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    with open(obj_path, "rb") as f:
        compressed_data = f.read()
    try:
        full_data = zlib.decompress(compressed_data)
    except zlib.error:
        typer.secho("Error: Failed to decompress Git object.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    try:
        header_end = full_data.index(b'\x00')
        header = full_data[:header_end].decode()
        content = full_data[header_end + 1:]
        obj_type, size_str = header.split()
        size = int(size_str)
    except Exception:
        typer.secho("Error: Invalid Git object format.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if len(content) != size:
        typer.secho("Error: Size mismatch in object.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if type:
        typer.echo(obj_type)
    elif pretty:
        if obj_type != "blob":
            typer.secho(f"Error: Pretty-print not supported for object type '{obj_type}'.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        typer.echo(content.decode(errors="replace"))