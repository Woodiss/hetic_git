
import os
from typing import List, Dict, Tuple
from git_scratch.utils.object import write_object
from git_scratch.utils.index_utils import load_index


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
                sub_oid = write_object(sub_tree, "tree")
                tree_entries[dir_name] = ("40000", bytes.fromhex(sub_oid))

    result = b""
    for name in sorted(tree_entries):
        mode, oid = tree_entries[name]
        result += f"{mode} {name}".encode() + b"\x00" + oid

    return result

def create_root_tree_object() -> str:
    """
    Loads the index, recursively builds the root Git tree object,
    stores it, and returns its OID.
    This function orchestrates the creation of the complete tree.
    """
    index_entries = load_index()
    if not index_entries:
        raise ValueError("Index is empty or not found. Nothing to commit.")

    # Utilise la fonction build_tree existante pour obtenir le contenu binaire du tree racine pour l'arbre racine, base_path est vide
    tree_content_bytes = build_tree(index_entries, base_path="")
    
    # Stocke cet objet tree racine dans le dépôt Git
    tree_oid = write_object(tree_content_bytes, "tree")
    
    return tree_oid