import os
from pathlib import Path
from typing import Optional

def get_head_commit_oid() -> Optional[str]:
    """
    Lit la référence HEAD et retourne l'OID du commit vers lequel elle pointe.
    Retourne None si HEAD n'existe pas (dépôt vide) ou si elle ne pointe nulle part.
    """
    head_path = Path(".git") / "HEAD"
    if not head_path.exists():
        return None # HEAD n'existe pas, probable dépôt vide

    with open(head_path, "r") as f:
        head_content = f.read().strip()

    if head_content.startswith("ref: "):
        # HEAD pointe vers une branche, ex: "ref: refs/heads/main"
        ref_name = head_content[len("ref: "):]
        ref_path = Path(".git") / ref_name
        if ref_path.exists():
            with open(ref_path, "r") as f_ref:
                return f_ref.read().strip() # Lit l'OID de la branche
        else:
            # La référence de branche n'existe pas (ex: branche toute neuve sans commit)
            return None
    else:
        # HEAD est en mode "detached HEAD", pointe directement vers un OID de commit
        # (Cela ne devrait pas arriver avec un 'commit' normal, mais on le gère)
        # Vérifie que c'est un OID valide (40 caractères hexadécimaux)
        if len(head_content) == 40 and all(c in "0123456789abcdef" for c in head_content):
            return head_content
        return None # Référence HEAD détachée invalide

def update_head_to_commit(new_commit_oid: str):
    """
    Met à jour la référence HEAD (et la branche actuelle qu'elle pointe)
    vers le nouvel OID du commit.
    """
    head_path = Path(".git") / "HEAD"
    
    if not head_path.exists() or not head_path.read_text().strip().startswith("ref: "):
        # Si HEAD n'existe pas ou n'est pas une référence de branche,
        # on assume qu'on doit créer/mettre à jour la branche 'main' (par défaut).
        # Un 'git init' plus complet devrait déjà configurer 'HEAD' pour pointer à 'main'.
        branch_ref_path = Path(".git") / "refs" / "heads" / "main"
        branch_ref_path.parent.mkdir(parents=True, exist_ok=True) # S'assure que le répertoire existe
        with open(branch_ref_path, "w") as f:
            f.write(new_commit_oid + "\n")
        # Et s'assure que HEAD pointe bien vers cette nouvelle branche
        with open(head_path, "w") as f:
            f.write("ref: refs/heads/main\n")
        return

    # HEAD est une référence de branche (ex: ref: refs/heads/ma_branche)
    with open(head_path, "r") as f:
        head_content = f.read().strip()

    # Extrait le chemin de la référence (ex: refs/heads/ma_branche)
    ref_name = head_content[len("ref: "):]
    ref_path = Path(".git") / ref_name
    
    ref_path.parent.mkdir(parents=True, exist_ok=True) # S'assure que le répertoire de la référence existe
    with open(ref_path, "w") as f:
        f.write(new_commit_oid + "\n")