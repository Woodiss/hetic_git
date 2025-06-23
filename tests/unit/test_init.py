import os
import pytest
from pathlib import Path
from typer.testing import CliRunner
from git_scratch.main import app
from subprocess import run

runner = CliRunner()


EXPECTED_PATHS = [
    "config",
    "description",
    "HEAD",
    "hooks",
    "info",
    "objects",
    "refs",
    "refs/heads",
    "refs/tags",
]

def test_pit_init(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    os.chdir(repo_path)

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    
    git_result = run(["git", "init"], cwd=repo_path, capture_output=True, text=True)
    assert git_result.returncode == 0

    expected_path = str(repo_path / ".git").replace("\\", "/")
    output = git_result.stdout.replace("\\", "/")

    assert "Reinitialized existing Git repository" in output
    assert expected_path in output

    git_dir = repo_path / ".git"
    assert git_dir.exists() and git_dir.is_dir()

    for relative_path in EXPECTED_PATHS:
        full_path = git_dir / relative_path
        assert full_path.exists(), f"Missing: {relative_path}"
