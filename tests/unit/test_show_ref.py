
import subprocess
import pytest
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

@pytest.fixture
def setup_fake_git(tmp_path):
    """
    Setup a minimal .git structure in a tempory folder.
    """
    git_dir = tmp_path / ".git"
    refs_heads = git_dir / "refs" / "heads"
    refs_remotes = git_dir / "refs" / "remotes" / "origin"

    refs_heads.mkdir(parents=True)
    refs_remotes.mkdir(parents=True)

    # Créer une ref locale
    (refs_heads / "main").write_text("1111111111111111111111111111111111111111")

    # Créer une ref distante
    (refs_remotes / "dev").write_text("2222222222222222222222222222222222222222")

    # Créer une ref symbolique
    head_path = git_dir / "refs" / "remotes" / "origin" / "HEAD"
    head_path.write_text("ref: refs/remotes/origin/dev")

    # Créer un fichier packed-refs avec une ref supplémentaire
    (git_dir / "packed-refs").write_text(
        """# pack-refs with: peeled fully-peeled
3333333333333333333333333333333333333333 refs/remotes/origin/feature
"""
    )

    return tmp_path

def test_show_ref_output(setup_fake_git, monkeypatch):
    # Redirige le répertoire courant vers notre dépôt temporaire
    monkeypatch.chdir(setup_fake_git)

    result = runner.invoke(app, ["show-ref"])
    assert result.exit_code == 0

    lines = result.output.strip().splitlines()
    assert "1111111111111111111111111111111111111111 refs/heads/main" in lines
    assert "2222222222222222222222222222222222222222 refs/remotes/origin/dev" in lines
    assert "2222222222222222222222222222222222222222 refs/remotes/origin/HEAD" in lines
    assert "3333333333333333333333333333333333333333 refs/remotes/origin/feature" in lines

    # Vérifie l'ordre lexicographique
    assert lines == sorted(lines)


def test_show_ref_matches_git_output(tmp_path, monkeypatch):
    # Initialiser un vrai dépôt Git
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("hello")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "checkout", "-b", "dev"], cwd=tmp_path, check=True)

    # Changer temporairement de répertoire courant
    monkeypatch.chdir(tmp_path)

    # Appeler ta commande pit show-ref
    result = runner.invoke(app, ["show-ref"])

    assert result.exit_code == 0

    pit_output = result.output.strip().splitlines()

    # Appeler git show-ref pour comparaison
    git_output = subprocess.check_output(["git", "show-ref"], cwd=tmp_path).decode().strip().splitlines()

    # Comparaison stricte
    assert sorted(pit_output) == sorted(git_output)
