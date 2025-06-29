
import os
import json
import stat
from pathlib import Path

def get_index_path():
    """
    Returns the path to the .git/index.json file based on the current directory.
    """
    return Path(os.getcwd()) / ".git" / "index.json"

def load_index():
    """
    Load the index.json file from .git/, or return an empty list if not found.
    """
    index_path = get_index_path()
    if not index_path.exists():
        return []

    with open(index_path, "r") as f:
        return json.load(f)

def save_index(index):
    """
    Save the given index to .git/index.json.
    """
    index_path = get_index_path()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

def compute_mode(file_path):
    """
    Compute the file mode as a string (e.g. '100644', '100755', '120000').
    """
    st = os.stat(file_path)
    if stat.S_ISLNK(st.st_mode):
        return "120000"
    elif st.st_mode & stat.S_IXUSR:
        return "100755"
    else:
        return "100644"

