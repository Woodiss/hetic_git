
import typer
from git_scratch.utils.read_object import read_object

def error(msg: str):
    typer.secho(f"Error: {msg}", fg=typer.colors.RED)
    raise typer.Exit(code=1)

def pretty_print_tree(content: bytes):
    i = 0
    while i < len(content):
        mode_end = content.find(b' ', i)
        name_end = content.find(b'\x00', mode_end)
        if mode_end == -1 or name_end == -1:
            error("Invalid tree object format.")

        mode = content[i:mode_end].decode()
        name = content[mode_end + 1:name_end].decode()
        sha = content[name_end + 1:name_end + 21].hex()
        type_ = "tree" if mode.startswith("40000") else "blob"

        typer.echo(f"{mode} {type_} {sha}\t{name}")
        i = name_end + 21

def cat_file(
    oid: str = typer.Argument(..., help="SHA-1 object ID to inspect."),
    type_opt: bool = typer.Option(False, "-t", help="Show the type of the object."),
    pretty: bool = typer.Option(False, "-p", help="Pretty-print the object’s content.")
):
    """
    Show information about a Git object by its OID.
    """
    if not (type_opt or pretty):
        error("You must specify either -t or -p.")

    if len(oid) != 40 or not all(c in "0123456789abcdef" for c in oid.lower()):
        error(f"Invalid OID format: {oid}")

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

    if type_opt:
        typer.echo(obj_type)
    elif pretty:
        if obj_type != "blob":
            typer.secho(f"Error: Pretty-print not supported for object type '{obj_type}'.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        typer.echo(content.decode(errors="replace"))