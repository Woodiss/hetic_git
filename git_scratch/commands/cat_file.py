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

    try:
        obj_type, content = read_object(oid)
    except FileNotFoundError:
        error(f"Object {oid} not found.")
    except Exception:
        error("Failed to read Git object.")

    if type_opt:
        typer.echo(obj_type)
    elif pretty:
        if obj_type in {"blob", "commit"}:
            typer.echo(content.decode(errors="replace"))
        elif obj_type == "tree":
            pretty_print_tree(content)
        else:
            error(f"Pretty-print not supported for object type '{obj_type}'.")
