
import os
import hashlib
import zlib
import typer
from typing import List, Dict, Tuple
from git_scratch.utils.index_utils import load_index

def store_object(data: bytes, type_: str) -> str:
    """
    Stocke un objet Git compressé et retourne son OID (SHA-1).
    """
    header = f"{type_} {len(data)}\0".encode()
    full_data = header + data
    oid = hashlib.sha1(full_data).hexdigest()

    obj_dir = os.path.join(".git", "objects", oid[:2])
    obj_path = os.path.join(obj_dir, oid[2:])
    os.makedirs(obj_dir, exist_ok=True)

    with open(obj_path, "wb") as f:
        f.write(zlib.compress(full_data))

    return oid

def build_tree(entries: List[Dict], base_path: str = "") -> bytes:
    tree_entries: Dict[str, Tuple[str, bytes]] = {}

    for entry in entries:
        rel_path = entry["path"]
        if not rel_path.startswith(base_path):
            continue

        sub_path = rel_path[len(base_path):].lstrip("/")
        parts = sub_path.split("/", 1)

        if len(parts) == 1:
            mode = entry["mode"]
            oid = bytes.fromhex(entry["oid"])
            name = parts[0]
            tree_entries[name] = (mode, oid)
        else:
            dir_name = parts[0]
            sub_base = os.path.join(base_path, dir_name)
            if dir_name not in tree_entries:
                sub_tree = build_tree(entries, sub_base)
                sub_oid = store_object(sub_tree, "tree")
                tree_entries[dir_name] = ("40000", bytes.fromhex(sub_oid))

    result = b""
    for name in sorted(tree_entries):
        mode, oid = tree_entries[name]
        result += f"{mode} {name}".encode() + b"\x00" + oid

    return result

def write_tree():
    """
    Writes a recursive Git tree from .git/index.json and displays its OID.
    """
    index = load_index()
    if not index:
        typer.secho("Erreur : .git/index.json not found or empty.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    tree_data = build_tree(index)
    oid = store_object(tree_data, "tree")
    typer.echo(oid)

