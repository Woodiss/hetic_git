import os
import subprocess
from pathlib import Path
import pytest
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

@pytest.fixture
def setup_repo_with_commit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    os.chdir(tmp_path)
    subprocess.run(["git", "init"], check=True)
    (tmp_path / "file.txt").write_text("hello\n")
    subprocess.run(["git", "add", "file.txt"], check=True)
    subprocess.run([
        "git", "-c", "user.name=Alice", "-c", "user.email=alice@example.com",
        "commit", "-m", "initial commit"
    ], check=True)

    # Fixer env pour pit avec même auteur/date
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Alice")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "alice@example.com")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Alice")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "alice@example.com")
    monkeypatch.setenv("GIT_AUTHOR_DATE", "1700000000 +0000")
    monkeypatch.setenv("GIT_COMMITTER_DATE", "1700000000 +0000")

    yield tmp_path

def parse_commit_content(content: str):
    lines = content.splitlines()
    data = {}
    message_lines = []
    in_message = False

    for line in lines:
        if in_message:
            message_lines.append(line)
        elif line == "":
            in_message = True
        else:
            if line.startswith("tree "):
                data["tree"] = line[len("tree "):]
            elif line.startswith("parent "):
                data["parent"] = line[len("parent "):]
            elif line.startswith("author "):
                author_info = " ".join(line.split(" ")[1:-2])
                data["author"] = author_info
            elif line.startswith("committer "):
                committer_info = " ".join(line.split(" ")[1:-2])
                data["committer"] = committer_info

    data["message"] = "\n".join(message_lines).strip()
    return data

def test_commit_content_similarity(setup_repo_with_commit: Path):
    tmp_path = setup_repo_with_commit

    git_oid = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    git_commit_content = subprocess.run(
        ["git", "cat-file", "-p", git_oid],
        capture_output=True, text=True, check=True
    ).stdout

    tree_oid = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    result = runner.invoke(
        app,
        ["commit-tree", tree_oid, "-m", "initial commit"],
        env=os.environ
    )
    assert result.exit_code == 0, f"Pit commit-tree failed: {result.stderr}"
    pit_oid = result.stdout.strip()

    pit_commit_content = subprocess.run(
        ["pit", "cat-file", "-p", pit_oid],
        capture_output=True, text=True, check=True
    ).stdout

    git_data = parse_commit_content(git_commit_content)
    pit_data = parse_commit_content(pit_commit_content)

    assert git_data["tree"] == pit_data["tree"], "Tree OID mismatch"
    assert git_data.get("parent") == pit_data.get("parent"), "Parent OID mismatch"
    assert git_data["author"] == pit_data["author"], "Author info mismatch"
    assert git_data["committer"] == pit_data["committer"], "Committer info mismatch"
    assert git_data["message"] == pit_data["message"], "Commit message mismatch"
