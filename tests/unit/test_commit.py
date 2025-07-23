import os
import subprocess
from pathlib import Path
import pytest
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

@pytest.fixture
def git_and_pit_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:

        # 3. Init Pit repo via CLI invoke (pour garder environnement Typer)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0, f"Pit init failed: {result.stderr}"

        # 1. Init Git repo via subprocess (plus fiable pour git natif)
        subprocess.run(["git", "init"], check=True)

        # 1bis. Fix permissions sur .git et sous-dossiers/fichiers pour éviter PermissionError
        git_dir = tmp_path / ".git"
        os.chmod(tmp_path, 0o755)
        for root, dirs, files in os.walk(git_dir):
            for d in dirs:
                os.chmod(Path(root) / d, 0o755)
            for f in files:
                os.chmod(Path(root) / f, 0o644)

        # 2. Configure Git user pour commit (important avant commit)
        subprocess.run(["git", "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], check=True)

        # 4. Créer un fichier de test
        (tmp_path / "test.txt").write_text("Hello test\n")
        
        # 6. Ajouter avec pit add via CLI (runner.invoke)
        result = runner.invoke(app, ["add", "test.txt"])
        assert result.exit_code == 0, f"Pit add failed: {result.stderr}"

        # 5. Ajouter avec git add via subprocess (pas besoin de pit ici)
        subprocess.run(["git", "add", "test.txt"], check=True)


        # 7. Commit git via subprocess (pour garder contrôle)
        subprocess.run([
            "git", "-c", "user.name=Test", "-c", "user.email=test@test.com",
            "commit", "-m", "hello"
        ], check=True)

        # 8. Monkeypatch env pour Pit commit
        monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
        monkeypatch.setenv("GIT_AUTHOR_EMAIL", "test@test.com")
        monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
        monkeypatch.setenv("GIT_COMMITTER_EMAIL", "test@test.com")
        monkeypatch.setenv("TZ", "UTC")

        # 9. Commit pit via CLI
        result = runner.invoke(app, ["commit", "-m", "hello"])
        assert result.exit_code == 0, f"Pit commit failed: {result.stderr}"

        yield tmp_path

    finally:
        os.chdir(old_cwd)


def test_commit_sha_matches_git(git_and_pit_repo: Path):
    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    pit_sha = subprocess.run(
        ["pit", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    assert git_sha == pit_sha, f"SHA mismatch: Git={git_sha}, Pit={pit_sha}"
