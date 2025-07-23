
import os
import shutil
import typer
from git_scratch.utils.checkout_utils import write_ref, list_working_dir_files, detect_dirty_workdir, read_tree, read_object, get_oid_from_ref, get_commit_tree, resolve_target_to_oid, restore_working_dir
from git_scratch.commands.reset import _get_tree_oid, entries_from_tree
from git_scratch.utils.index_utils import save_index

def resolve_target_to_oid(target: str) -> str | None:
    """
    Résout un target (branche ou SHA) vers un OID.
    """
    # 1. Si c'est une branche
    branch_ref_path = os.path.join(".git", "refs", "heads", target)
    if os.path.exists(branch_ref_path):
        with open(branch_ref_path) as f:
            return f.read().strip()

    # 2. Si c'est un SHA direct (40 hex chars)
    if len(target) == 40 and all(c in "0123456789abcdef" for c in target.lower()):
        return target

    return None


def create_branch(branch_name: str, oid: str):
    """
    Crée une nouvelle branche dans .git/refs/heads/<branch_name>
    """
    branch_ref_path = os.path.join(".git", "refs", "heads", branch_name)
    if os.path.exists(branch_ref_path):
        typer.secho(f"fatal: branch '{branch_name}' already exists", fg=typer.colors.RED)
        raise typer.Exit(1)
    with open(branch_ref_path, "w") as f:
        f.write(oid)


def checkout_tree(tree_oid: str):
    """
    Checkout du tree dans le working dir : écrase les fichiers
    """
    # Lire le tree complet
    tree_entries = read_tree(tree_oid)

    # Nettoyer les fichiers du working dir (sauf .git)
    for f in list_working_dir_files():
        if not f.startswith(".git"):
            os.remove(f)

    # Extraire chaque blob dans le working dir
    for path, (mode, oid) in tree_entries.items():
        obj_type, content = read_object(oid)
        if obj_type != "blob":
            continue  # ignore subtrees for now (pas encore de dossiers)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)


def write_HEAD_ref(value: str):
    """
    Met à jour HEAD : soit `ref: refs/heads/...` soit un SHA brut
    """
    with open(".git/HEAD", "w") as f:
        f.write(value + "\n")


def is_branch(name: str) -> bool:
    return os.path.exists(os.path.join(".git", "refs", "heads", name))

def update_index_from_commit(commit_oid: str):
    """
    Met à jour l'index.json en fonction du tree du commit.
    """
    tree_oid = _get_tree_oid(commit_oid)
    new_index = entries_from_tree(tree_oid)
    save_index(new_index)

def checkout(
    target: str = typer.Argument(None, help="Branch or commit to checkout"),
    b: str = typer.Option(None, "-b", help="Create a new branch"),
    start_point: str = typer.Argument(None, help="Optional start-point for -b")
):
    """
    pit checkout [-b <branch>] [<commit|branch>]
    """
    # --- Mode création de branche ---
    if b:
        new_branch = b
        base_oid = start_point if start_point else get_oid_from_ref("HEAD")

        # Vérifier que base_oid existe
        try:
            obj_type, _ = read_object(base_oid)
        except FileNotFoundError:
            typer.secho(f"Base {base_oid} not found", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Créer la branche
        ref_path = os.path.join(".git", "refs", "heads", new_branch)
        if os.path.exists(ref_path):
            typer.secho(f"Branch '{new_branch}' already exists!", fg=typer.colors.RED)
            raise typer.Exit(1)
        write_ref(ref_path, base_oid)

        # Mettre HEAD sur la nouvelle branche
        with open(".git/HEAD", "w") as f:
            f.write(f"ref: refs/heads/{new_branch}\n")

        typer.secho(f"Switched to a new branch '{new_branch}'", fg=typer.colors.GREEN)
        # On restaure le workdir du commit
        restore_working_dir(base_oid)
        update_index_from_commit(base_oid)
        return

    # --- Sinon, checkout normal ---
    if not target:
        typer.secho("You must provide a target branch or commit", fg=typer.colors.RED)
        raise typer.Exit(1)

    oid = resolve_target_to_oid(target)

    # 🔴 Gestion du cas inexistant
    if oid is None:
        typer.secho(f"error: pathspec '{target}' did not match any branch or commit", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Vérifier dirty working dir
    if detect_dirty_workdir():
        typer.secho("Your working directory has uncommitted changes!", fg=typer.colors.RED)
        raise typer.Exit(1)

    # HEAD doit pointer sur la branche si elle existe, sinon commit détaché
    branch_ref = os.path.join(".git", "refs", "heads", target)
    if os.path.exists(branch_ref):
        with open(".git/HEAD", "w") as f:
            f.write(f"ref: refs/heads/{target}\n")
    else:
        # HEAD détaché
        with open(".git/HEAD", "w") as f:
            f.write(oid + "\n")

    typer.secho(f"Checked out {target}", fg=typer.colors.GREEN)
    restore_working_dir(oid)
    update_index_from_commit(oid)
