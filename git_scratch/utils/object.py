import os
import hashlib
import zlib

def write_object(content: bytes, obj_type: str) -> str:
    """
    Write a Git object to the .git/objects directory.

    Args:
        content (bytes): Raw content of the object (e.g. file data, commit, tree).
        obj_type (str): Type of the object: 'blob', 'tree', or 'commit'.

    Returns:
        str: The SHA-1 object ID (OID) of the written object.
    """
    if obj_type not in {"blob", "tree", "commit"}:
        raise ValueError(f"Invalid object type: {obj_type}")

    header = f"{obj_type} {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()

    dir_path = os.path.join(".git", "objects", oid[:2])
    file_path = os.path.join(dir_path, oid[2:])

    if os.path.exists(file_path):
        return oid

    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(zlib.compress(full_data))

    return oid