
import hashlib

def compute_blob_hash(content: bytes) -> tuple[str, bytes]:
    header = f"blob {len(content)}\0".encode()
    full_data = header + content
    oid = hashlib.sha1(full_data).hexdigest()
    return oid, full_data
