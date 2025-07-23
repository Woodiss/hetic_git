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
        subprocess.run(["pit", "init"], check=True)

        (tmp_path / "test.txt").write_text("Hello test\n")
        subprocess.run(["git", "add", "test.txt"], check=True)
        subprocess.run(["pit", "add", "test.txt"], check=True)

        subprocess.run([
            "git", "-c", "user.name=Test", "-c", "user.email=test@test.com",
            "commit", "-m", "hello"
        ], check=True)

        monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
        monkeypatch.setenv("GIT_AUTHOR_EMAIL", "test@test.com")
        monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
        monkeypatch.setenv("GIT_COMMITTER_EMAIL", "test@test.com")
        monkeypatch.setenv("TZ", "UTC")

        result = runner.invoke(app, ["commit", "-m", "hello"])
        assert result.exit_code == 0, f"Commit Pit failed: {result.stderr}"

        yield tmp_path

    finally:
        os.chdir(old_cwd)


def test_commit_sha_matches_git(git_and_pit_repo: Path):

    git_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    pit_sha = subprocess.run(["pit", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()

    assert git_sha == pit_sha, f"SHA mismatch: Git={git_sha}, Pit={pit_sha}"
