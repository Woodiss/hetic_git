import os
import zlib

def read_object(oid: str) -> tuple[str, bytes]:
    """
    Read and decompress a Git object by its OID.
    Returns:
        - type (e.g., 'tree', 'blob')
        - content (raw bytes after header)
    """
    path = os.path.join(".git", "objects", oid[:2], oid[2:])
    if not os.path.exists(path):
        raise FileNotFoundError(f"Object {oid} not found.")

    with open(path, "rb") as f:
        compressed = f.read()

    data = zlib.decompress(compressed)
    header_end = data.index(b"\x00")
    header = data[:header_end].decode()
    obj_type, _ = header.split()
    content = data[header_end + 1:]
    return obj_type, content
