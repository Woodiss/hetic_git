import os
import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from git_scratch.main import app
from git_scratch.commands.status import git_hash_object
from git_scratch.utils.index_utils import get_index_path

@pytest.fixture

def runner(tmp_path, monkeypatch):
    """
    Fournit un CliRunner configuré dans un dépôt Git simulé.
    """
    # Change le répertoire courant vers tmp_path
    monkeypatch.chdir(tmp_path)
    # Crée un dossier .git et un index vide
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "index.json").write_text("[]")
    # Retourne le runner Typer
    return CliRunner()


def test_status_no_change(runner):
    # Aucun changement dans le dépôt
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "aucun fichier modifié détecté" in result.stdout.lower()


def test_status_shows_modified_file(runner):
    # Crée et indexe un fichier tracké puis le modifie
    tracked = Path("tracked.txt")
    tracked.write_text("version 1")
    oid = git_hash_object(str(tracked))
    idx = get_index_path()
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text(json.dumps([{"path": str(tracked), "oid": oid}]))
    # Modification du fichier
    tracked.write_text("version 2")
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    out = result.stdout.lower()
    assert "modified" in out
    assert "tracked.txt" in out


def test_status_shows_untracked_file(runner):
    # Crée un fichier non tracké
    untracked = Path("new_file.txt")
    untracked.write_text("content")
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    out = result.stdout.lower()
    assert "untracked" in out
    assert "new_file.txt" in out


def test_status_multiple_changes(runner):
    # Fichier tracké modifié
    tracked = Path("t1.txt")
    tracked.write_text("v1")
    oid = git_hash_object(str(tracked))
    idx = get_index_path()
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text(json.dumps([{"path": str(tracked), "oid": oid}]))
    tracked.write_text("v2")
    # Fichier non tracké
    untracked = Path("u1.txt")
    untracked.write_text("u")
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    out = result.stdout.lower()
    assert "modified" in out and "t1.txt" in out
    assert "untracked" in out and "u1.txt" in out
