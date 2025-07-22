from pathlib import Path
import pathspec

def load_gitignore_spec():
    """
    Charge les règles de .gitignore en utilisant pathspec.
    Retourne un objet PathSpec utilisable pour ignorer les fichiers.
    """
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    return pathspec.PathSpec.from_lines("gitwildmatch", [])

def is_ignored(path: str, spec=None) -> bool:
    """
    Vérifie si un chemin correspond à une règle de .gitignore.
    """
    if spec is None:
        spec = load_gitignore_spec()
    return spec.match_file(path)