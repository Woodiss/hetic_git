import os
import subprocess
from pathlib import Path
from typer.testing import CliRunner
from git_scratch.main import app  # adapte selon où est défini ton Typer app

runner = CliRunner()

def init_test_repo(tmp_path: Path):
    """
    Initialise un repo git temporaire avec 2 commits.
    """
    os.chdir(tmp_path)

    # Init repo
    subprocess.run(["git", "init"], check=True)

    # Commit 1
    (tmp_path / "file1.txt").write_text("Hello World")
    subprocess.run(["git", "add", "file1.txt"], check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test User", "-c", "user.email=test@example.com",
         "commit", "-m", "Initial commit"],
        check=True
    )

    # Commit 2
    (tmp_path / "file2.txt").write_text("Another file")
    subprocess.run(["git", "add", "file2.txt"], check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test User", "-c", "user.email=test@example.com",
         "commit", "-m", "Second commit"],
        check=True
    )


def test_pit_log_matches_git_log(tmp_path):
    # 1. Créer un repo de test avec deux commits
    init_test_repo(tmp_path)

    # 2. Récupère la sortie officielle de git log
    git_output = subprocess.run(
        ["git", "log", "--no-decorate", "--no-color"],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path
    ).stdout.strip()

    # 3. Exécute pit log dans le même repo
    # On change le cwd pour être dans le repo test
    os.chdir(tmp_path)
    result = runner.invoke(app, ["log"])
    pit_output = result.stdout.strip()

    # Debug si ça diffère
    if git_output != pit_output:
        print("\n=== GIT LOG ===")
        print(git_output)
        print("\n=== PIT LOG ===")
        print(pit_output)

    # 4. Vérifie que les deux sorties sont identiques
    assert pit_output == git_output
