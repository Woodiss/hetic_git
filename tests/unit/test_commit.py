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
        subprocess.run(["git", "init"], check=True)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0, f"Pit init failed: {result.stderr}"

        (tmp_path / "test.txt").write_text("Hello test\n")

        subprocess.run(["git", "add", "test.txt"], check=True)

        result = runner.invoke(app, ["add", "test.txt"])
        assert result.exit_code == 0, f"Pit add failed: {result.stderr}"

        subprocess.run([
            "git", "-c", "user.name=Test", "-c", "user.email=test@test.com",
            "commit", "-m", "hello"
        ], check=True)

        # Fix env variables for pit commit to match git commit
        monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
        monkeypatch.setenv("GIT_AUTHOR_EMAIL", "test@test.com")
        monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
        monkeypatch.setenv("GIT_COMMITTER_EMAIL", "test@test.com")
        monkeypatch.setenv("GIT_AUTHOR_DATE", "1700000000 +0000")
        monkeypatch.setenv("GIT_COMMITTER_DATE", "1700000000 +0000")
        monkeypatch.setenv("TZ", "UTC")

        result = runner.invoke(app, ["commit", "-m", "hello"])
        assert result.exit_code == 0, f"Pit commit failed: {result.stderr}"

        yield tmp_path

    finally:
        os.chdir(old_cwd)


def test_commit_sha_matches_git(git_and_pit_repo: Path):
    # Use subprocess for git rev-parse (git must be available)
    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    # Use runner.invoke for pit rev-parse to keep consistency
    result = runner.invoke(app, ["rev-parse", "HEAD"])
    assert result.exit_code == 0, f"Pit rev-parse failed: {result.stderr}"
    pit_sha = result.stdout.strip()

    assert git_sha == pit_sha, f"SHA mismatch: Git={git_sha}, Pit={pit_sha}"
