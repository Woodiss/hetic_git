import os
import json
from pathlib import Path
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

def test_rmfile_removes_file_and_index(tmp_path):
    # Crée un faux repo temporaire avec un .git
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    index_file = git_dir / "index.json"

    # Crée un fichier à supprimer
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")

    # Ajoute l'entrée dans l'index simulé
    index_data = [
        {
            "mode": "100644",
            "oid": "fake_oid_for_test",
            "path": "test.txt"
        }
    ]
    index_file.write_text(json.dumps(index_data, indent=2))

    # Se place dans le bon dossier pour exécuter le test
    os.chdir(tmp_path)

    # Appelle pit rm test.txt
    result = runner.invoke(app, ["rm", "test.txt"])

    # Vérifie que le fichier a bien été supprimé
    assert not file_path.exists()

    # Vérifie que l'entrée a bien été retirée de l'index
    updated_index = json.loads(index_file.read_text())
    assert updated_index == []

    # Vérifie le message en sortie
    assert "removed from working directory" in result.output
    assert "removed from staging area" in result.output

def test_rmfile_file_not_in_index(tmp_path):
    # Crée un faux repo temporaire avec un .git
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    index_file = git_dir / "index.json"

    # Crée un fichier qui va être supprimé
    file_path = tmp_path / "orphan.txt"
    file_path.write_text("I'm not in the index")

    # Initialise l’index avec un autre fichier seulement
    index_data = [
        {
            "mode": "100644",
            "oid": "some_other_oid",
            "path": "not_me.txt"
        }
    ]
    index_file.write_text(json.dumps(index_data, indent=2))

    # Se place dans le bon dossier
    os.chdir(tmp_path)

    # Appelle pit rm orphan.txt
    result = runner.invoke(app, ["rm", "orphan.txt"])

    # Vérifie que le fichier a bien été supprimé
    assert not file_path.exists()

    # L’index ne doit pas avoir changé
    updated_index = json.loads(index_file.read_text())
    assert updated_index == index_data

    # Vérifie que l'on a bien le bon message
    assert "removed from working directory" in result.output
    assert "was not in the index" in result.output

def test_rmfile_file_not_found(tmp_path):
    # Crée un faux repo temporaire avec un .git
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    index_file = git_dir / "index.json"

    # Initialise l’index avec un fichier
    index_data = [
        {
            "mode": "100644",
            "oid": "some_oid",
            "path": "existing.txt"
        }
    ]
    index_file.write_text(json.dumps(index_data, indent=2))

    # Se place dans le bon dossier
    os.chdir(tmp_path)

    # Appelle pit rm non_existent.txt
    result = runner.invoke(app, ["rm", "non_existent.txt"])

    # Vérifie que le message d'erreur est correct
    assert "does not exist in working directory" in result.output

    # L’index ne doit pas avoir changé
    updated_index = json.loads(index_file.read_text())
    assert updated_index == index_data