
import hashlib
import os
import zlib

def compute_blob_hash(content: bytes) -> tuple[str, bytes]:
    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()
    return oid, full_data

def write_object(oid: str, full_data: bytes):
    obj_dir = os.path.join(".git", "objects", oid[:2])
    obj_path = os.path.join(obj_dir, oid[2:])
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_path, "wb") as f:
        f.write(zlib.compress(full_data))
