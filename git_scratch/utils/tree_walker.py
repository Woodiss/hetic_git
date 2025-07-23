from git_scratch.utils.read_object import read_object
from typing import List
import os

def entries_from_tree(tree_oid: str, base_path: str = "") -> List[dict]:
    """Walk *tree_oid* recursively and return index‑style dict entries."""
    entries: List[dict] = []
    obj_type, content = read_object(tree_oid)
    if obj_type != "tree":
        raise ValueError("Expected tree object")

    i = 0
    while i < len(content):
        mode_end = content.find(b" ", i)
        name_end = content.find(b"\x00", mode_end)
        mode = content[i:mode_end].decode()
        name = content[mode_end + 1 : name_end].decode()
        oid_bytes = content[name_end + 1 : name_end + 21]
        oid = oid_bytes.hex()
        i = name_end + 21

        rel_path = os.path.join(base_path, name)
        if mode == "40000":  # subtree
            entries.extend(entries_from_tree(oid, rel_path))
        else:
            entries.append({"path": rel_path, "oid": oid, "mode": mode})

    return entries