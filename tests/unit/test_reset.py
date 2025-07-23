import subprocess
from pathlib import Path
from git_scratch.utils.tree_walker import entries_from_tree
from git_scratch.commands.reset import _get_tree_oid

# Create a temporary Git repository with two commits
def init_test_repo(tmp_path: Path) -> tuple[Path, list[str]]:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    file = tmp_path / "file.txt"
    file.write_text("version 1")
    subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=T", "-c", "user.email=t@example.com",
         "commit", "-m", "commit A"],
        cwd=tmp_path, check=True
    )

    file.write_text("version 2")
    subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=T", "-c", "user.email=t@example.com",
         "commit", "-m", "commit B"],
        cwd=tmp_path, check=True
    )

    commits = subprocess.check_output(
        ["git", "rev-list", "--max-count", "2", "HEAD"],
        cwd=tmp_path).decode().splitlines()
    return tmp_path, commits

# Get the SHA of the current branch in a Git repository
def current_branch_sha(repo: Path) -> str:
    # master ou main selon Git
    for branch in ("master", "main"):
        ref = repo / ".git/refs/heads" / branch
        if ref.exists():
            return ref.read_text().strip()
    raise RuntimeError("branche introuvable")

def blob_oid_at_path(commit_oid: str, file_path: str) -> str:
    tree_oid = _get_tree_oid(commit_oid)
    for e in entries_from_tree(tree_oid):
        if e["path"] == file_path:
            return e["oid"]
    raise KeyError(f"{file_path} absent du commit {commit_oid}")

# Test cases for the `pit reset` command
def test_soft_reset(tmp_path):
    repo, commits = init_test_repo(tmp_path)
    subprocess.run(["pit", "reset", commits[1], "--soft"], cwd=repo, check=True)

    assert current_branch_sha(repo) == commits[1]
    assert (repo / "file.txt").read_text() == "version 2"

# Test cases for the `pit mixed` command
def test_mixed_reset(tmp_path):
    repo, commits = init_test_repo(tmp_path)
    subprocess.run(["pit", "reset", commits[1], "--mixed"], cwd=repo, check=True)

    assert current_branch_sha(repo) == commits[1]
    assert (repo / "file.txt").read_text() == "version 2"

# Test cases for the `pit hard` command
def test_hard_reset(tmp_path):
    repo, commits = init_test_repo(tmp_path)
    subprocess.run(["pit", "reset", commits[1], "--hard"], cwd=repo, check=True)

    assert current_branch_sha(repo) == commits[1]
    assert (repo / "file.txt").read_text() == "version 1"
