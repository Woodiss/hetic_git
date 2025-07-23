
import zlib
import os

def read_object(oid: str):
    """
    Lit un objet Git compressé et renvoie (type, content).
    """
    path = os.path.join(".git", "objects", oid[:2], oid[2:])
    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

    header, content = raw.split(b"\x00", 1)
    obj_type = header.split()[0].decode()
    return obj_type, content


def get_oid_from_ref(ref_name: str) -> str:
    """
    Résout HEAD en OID (commit SHA)
    """
    head_path = os.path.join(".git", "HEAD")
    with open(head_path) as f:
        data = f.read().strip()

    # HEAD symbolique -> lire refs/heads/<branch>
    if data.startswith("ref:"):
        ref_path = os.path.join(".git", data[5:])
        with open(ref_path) as rf:
            return rf.read().strip()
    else:
        return data  # HEAD détaché


def get_commit_tree(commit_oid):
    """Récupère le tree d'un commit"""
    obj_type, content = read_object(commit_oid)
    assert obj_type == "commit"
    first_line = content.decode().split("\n")[0]
    return first_line.split(" ")[1]


def read_tree(tree_oid: str) -> dict:
    obj_type, content = read_object(tree_oid)
    assert obj_type == "tree", f"Expected tree, got {obj_type}"

    i = 0
    entries = {}
    while i < len(content):
        # format : <mode> <name>\0<20-byte sha>
        end_mode = content.find(b" ", i)
        mode = content[i:end_mode].decode()
        end_name = content.find(b"\x00", end_mode)
        name = content[end_mode+1:end_name].decode()
        sha_raw = content[end_name+1:end_name+21]
        oid = sha_raw.hex()
        entries[name] = (mode, oid)
        i = end_name + 21
    return entries

def read_tree_files(tree_oid, base_path=""):
    """
    Retourne un dict {path: blob_oid} de tous les fichiers d'un tree récursif
    """
    obj_type, content = read_object(tree_oid)
    assert obj_type == "tree", f"Expected tree, got {obj_type}"
    
    files = {}
    i = 0
    while i < len(content):
        mode_end = content.find(b' ', i)
        mode = content[i:mode_end].decode()
        name_end = content.find(b'\x00', mode_end)
        name = content[mode_end+1:name_end].decode()
        oid = content[name_end+1:name_end+21].hex()
        i = name_end + 21

        path = os.path.join(base_path, name) if base_path else name
        if mode.startswith("40000"):  # tree (dossier)
            files.update(read_tree_files(oid, path))
        else:  # blob (fichier)
            files[path] = oid

    return files
def list_working_dir_files():
    """Liste tous les fichiers du working dir en ignorant .git"""
    tracked = []
    for root, dirs, files in os.walk("."):
        if root.startswith("./.git"):
            continue
        for f in files:
            path = os.path.join(root, f)[2:]  # enlève ./ au début
            tracked.append(path)
    return tracked


def detect_dirty_workdir():
    """
    Retourne True si le working dir a des changements par rapport au HEAD.
    - Ignore .git
    - Ignore les fichiers non trackés
    """
    head_ref_path = os.path.join(".git", "HEAD")
    if not os.path.exists(head_ref_path):
        return False  # pas encore de commit => pas dirty
    
    with open(head_ref_path) as f:
        ref = f.read().strip()
    
    if ref.startswith("ref:"):
        ref_path = os.path.join(".git", ref[5:])
        if not os.path.exists(ref_path):
            return False
        with open(ref_path) as f:
            head_oid = f.read().strip()
    else:
        head_oid = ref

    if not head_oid:
        return False  # repo vide => pas dirty

    # Récupérer le tree du HEAD
    tree_oid = get_commit_tree(head_oid)
    tracked_files = read_tree_files(tree_oid)

    # Lister les fichiers du working dir
    wd_files = list_working_dir_files()

    for path in tracked_files:
        # Si le fichier n'existe plus => dirty
        if path not in wd_files:
            return True

        # Comparer le contenu
        obj_type, blob_content = read_object(tracked_files[path])
        with open(path, "rb") as f:
            wd_content = f.read()

        if blob_content != wd_content:
            return True  # diff détectée

    return False  # identique au HEAD


def write_ref(ref_path: str, oid: str):
    """
    Écrit un OID dans un fichier ref.
    """
    with open(ref_path, "w") as f:
        f.write(oid + "\n")


def resolve_target_to_oid(target: str) -> str:
    """
    Si target est une branche, retourne son commit. Si c'est un SHA, retourne tel quel.
    """
    branch_ref = os.path.join(".git", "refs", "heads", target)
    if os.path.exists(branch_ref):
        with open(branch_ref) as f:
            return f.read().strip()
    else:
        # supposons que c'est un commit sha
        return target

def restore_working_dir(commit_oid: str):
    """
    Remet le working dir à l'état du commit (pour l'instant supprime tout et réécrit)
    """
    tree_oid = get_commit_tree(commit_oid)
    entries = read_tree(tree_oid)

    # Nettoyage
    for f in list_working_dir_files():
        os.remove(f)

    # Réécriture
    for path, (mode, blob_oid) in entries.items():
        obj_type, blob_content = read_object(blob_oid)
        assert obj_type == "blob"
        with open(path, "wb") as f:
            f.write(blob_content)
