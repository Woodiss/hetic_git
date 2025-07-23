from pathlib import Path

def find_git_dir(start_path: Path = Path.cwd()) -> Path:
    """
    Remonte l'arborescence depuis `start_path` jusqu'à trouver un dossier `.git`.
    Renvoie le chemin absolu vers `.git`, ou lève une FileNotFoundError si non trouvé.
    """
    path = start_path.resolve()
    while True:
        git_path = path / ".git"
        if git_path.is_dir():
            return git_path

        parent = path.parent
        if parent == path:
            # On est à la racine du système
            raise FileNotFoundError("No .git directory found.")
        path = parent