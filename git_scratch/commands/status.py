import hashlib
import os
import time
from pathlib import Path
from typing import List, Tuple

import pathspec
import typer

from git_scratch.utils.gitignore_utils import is_ignored, load_gitignore_spec
from git_scratch.utils.index_utils import load_index
from git_scratch.utils.read_object import read_object
from git_scratch.utils.tree_walker import entries_from_tree


def get_head_tree_oid() -> str:
    """
    Lit la référence HEAD et renvoie l'OID du tree du dernier commit.
    """
    head_content = Path('.git/HEAD').read_text().strip()
    if head_content.startswith('ref: '):
        ref_path = Path('.git') / head_content[5:]
        commit_oid = ref_path.read_text().strip()
    else:
        commit_oid = head_content

    obj_type, commit_data = read_object(commit_oid)
    if obj_type != 'commit':
        raise ValueError(f"OID {commit_oid} is not a commit (got {obj_type})")

    for line in commit_data.split(b'\n'):
        if line.startswith(b'tree '):
            return line.split()[1].decode()
    raise ValueError('Missing tree entry in commit')


def git_hash_object(file_path: Path) -> str:
    """
    Calcule le SHA-1 Git d'un fichier blob.
    """
    data = file_path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def list_project_files() -> List[str]:
    """
    Parcourt récursivement le projet et renvoie les chemins de tous fichiers hors .git.
    """
    return [str(p) for p in Path('.')
            .rglob('*')
            if p.is_file() and '.git' not in p.parts]


def print_section(title: str, entries: List[Tuple[str, str]], color: str) -> None:
    """
    Affiche une section de status avec un titre et des paires (action, chemin).
    """
    typer.echo(typer.style(title, fg=color))
    for action, path in entries:
        typer.echo(typer.style(f'  {action:>9} {path}', fg=color))
    typer.echo()


def status() -> None:
    """
    Implémentation de la commande `pit status`:
    - Compare HEAD vs index (staged)
    - Compare index vs working directory (unstaged)
    - Liste les fichiers non suivis
    """
    start = time.time()

    head_tree_oid = get_head_tree_oid()
    commit_entries = {e['path']: e['oid'] for e in entries_from_tree(head_tree_oid)}

    index_list = load_index()
    print("==== INDEX ENTRIES ====")
    for item in index_list:
        print(item["path"])
    print("=======================")
    index_entries = {item['path']: item['oid'] for item in index_list}

    spec = load_gitignore_spec()

    staged: List[Tuple[str, str]] = []
    unstaged: List[Tuple[str, str]] = []
    untracked: List[Tuple[str, str]] = []

    for fpath_str in list_project_files():
        if spec.match_file(fpath_str) or is_ignored(fpath_str, spec):
            continue

        in_index = fpath_str in index_entries
        in_commit = fpath_str in commit_entries

        if in_index:
            oid_idx = index_entries[fpath_str]
            if not in_commit:
                staged.append(('new file', fpath_str))
            elif commit_entries[fpath_str] != oid_idx:
                staged.append(('modified', fpath_str))
        else:
            if not in_commit:
                untracked.append(('?', fpath_str))

    for path in commit_entries:
        if path not in index_entries:
            staged.append(('deleted', path))

    for path, oid in index_entries.items():
        fpath = Path(path)
        if not fpath.exists():
            unstaged.append(('deleted', path))
        else:
            if git_hash_object(fpath) != oid:
                unstaged.append(('modified', path))

    if staged:
        print_section('Changes to be committed:\n (use "pit reset <file>..." to unstage)\n', staged, typer.colors.GREEN)
    if unstaged:
        print_section('Changes not staged for commit:\n (use "pit add <file>..." to update what will be committed)\n (use "pit restore <file>..." to discard changes in working directory)\n', unstaged, typer.colors.RED)
    if untracked:
        print_section('Untracked files:\n (use "pit add <file>..." to include in what will be committed)\n', untracked, typer.colors.RED)
    if not (staged or unstaged or untracked):
        typer.echo("Rien à valider, l'arbre et l'index sont à jour.")

    typer.echo(f"Temps total: {time.time() - start:.3f}s")