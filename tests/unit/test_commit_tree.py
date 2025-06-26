import os
import json
import subprocess
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

def test_commit_tree_oid_matches_git(tmp_path):
    """
    Vérifie que pit commit-tree retourne le même OID que git commit-tree
    """
    # Aller dans le bon dossier temporaire
    os.chdir(tmp_path)

    # Initialiser le dépôt avec pit
    result_init = runner.invoke(app, ["init"])
    assert result_init.exit_code == 0

    # Créer un fichier
    file = tmp_path / "file.txt"
    content = "Hello Commit Tree"
    file.write_text(content)

    # Ajouter avec Git
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "add", "file.txt"], check=True)
    result_tree = subprocess.run(["git", "write-tree"], capture_output=True, text=True, check=True)
    tree_oid_git = result_tree.stdout.strip()

    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "TestUser",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "TestUser",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    })
    result_commit = subprocess.run(
        ["git", "commit-tree", tree_oid_git, "-m", "Initial commit"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    commit_oid_git = result_commit.stdout.strip()

    # Créer index.json pour pit
    index_path = tmp_path / ".git" / "index.json"
    oid = runner.invoke(app, ["hash-object", "file.txt", "--write"]).stdout.strip()
    index_path.write_text(json.dumps([
        {
            "path": "file.txt",
            "oid": oid,
            "mode": "100644"
        }
    ]))

    # Générer avec pit
    tree_oid_pit = runner.invoke(app, ["write-tree"]).stdout.strip()
    commit_oid_pit = runner.invoke(app, [
        "commit-tree", tree_oid_pit, "-m", "Initial commit"
    ]).stdout.strip()

    assert tree_oid_pit == tree_oid_git
    assert commit_oid_pit == commit_oid_git
