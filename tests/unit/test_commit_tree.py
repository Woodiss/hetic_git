import os
import subprocess
from pathlib import Path
import pytest
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

@pytest.fixture
def git_and_pit_repo_for_commit_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], check=True)

        git_dir = tmp_path / ".git"
        os.chmod(tmp_path, 0o755)
        for root, dirs, files in os.walk(git_dir):
            for d in dirs:
                os.chmod(Path(root) / d, 0o755)
            for f in files:
                os.chmod(Path(root) / f, 0o644)

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0, f"Pit init failed: {result.stderr}"

        (tmp_path / "test.txt").write_text("Hello commit-tree\n")
        result = runner.invoke(app, ["add", "test.txt"])
        assert result.exit_code == 0, f"Pit add failed: {result.stderr}"
        subprocess.run(["git", "add", "test.txt"], check=True)

        subprocess.run([
            "git", "-c", "user.name=Test", "-c", "user.email=test@test.com",
            "commit", "-m", "initial commit"
        ], check=True)

        monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
        monkeypatch.setenv("GIT_AUTHOR_EMAIL", "test@test.com")
        monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
        monkeypatch.setenv("GIT_COMMITTER_EMAIL", "test@test.com")
        monkeypatch.setenv("TZ", "UTC")

        yield tmp_path
    finally:
        os.chdir(old_cwd)

def test_pit_commit_tree(git_and_pit_repo_for_commit_tree: Path):
    result = runner.invoke(app, ["write-tree"])
    assert result.exit_code == 0, f"Pit write-tree failed: {result.stderr}"
    tree_oid = result.stdout.strip()
    assert len(tree_oid) == 40, "Tree OID should be 40 characters SHA-1"

    parent_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    result = runner.invoke(app, ["commit-tree", tree_oid, "-p", parent_sha, "-m", "commit-tree test"])
    assert result.exit_code == 0, f"Pit commit-tree failed: {result.stderr}"
    commit_oid = result.stdout.strip()
    assert len(commit_oid) == 40, "Commit OID should be 40 characters SHA-1"

    git_commit_oid = subprocess.run(
        ["git", "rev-parse", commit_oid], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert commit_oid == git_commit_oid, "Commit OID not found by git rev-parse"
