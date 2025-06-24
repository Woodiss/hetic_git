import json
import zlib
import hashlib
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()

def setup_git_repo(tmp_path):
    git_dir = tmp_path / ".git"
    objects_dir = git_dir / "objects"
    objects_dir.mkdir(parents=True)

    entries = [
        {
            "mode": "100644",
            "oid": hashlib.sha1(b"blob 11\0hello world").hexdigest(),
            "path": "hello.txt"
        }
    ]

    obj_path = objects_dir / entries[0]["oid"][:2] / entries[0]["oid"][2:]
    obj_path.parent.mkdir(exist_ok=True)
    with open(obj_path, "wb") as f:
        compressed = zlib.compress(b"blob 11\0hello world")
        f.write(compressed)

    index_path = git_dir / "index.json"
    with open(index_path, "w") as f:
        json.dump(entries, f)

    return git_dir

def test_write_tree(tmp_path, monkeypatch):
    git_dir = setup_git_repo(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["write-tree"])
    assert result.exit_code == 0, f"CLI failed with exit code {result.exit_code}"
    assert "Tree OID: " in result.stdout, "Expected Tree OID in CLI output"
    oid = result.stdout.strip().split()[-1]

    obj_path = git_dir / "objects" / oid[:2] / oid[2:]
    assert obj_path.exists(), f"Tree object file does not exist at {obj_path}"
