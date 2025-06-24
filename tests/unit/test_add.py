from typer.testing import CliRunner
import hashlib
import json
import os

from git_scratch.main import app

runner = CliRunner()

def test_add_creates_object_and_index_entry(tmp_path):

    git_dir = tmp_path / ".git"
    objects_dir = git_dir / "objects"
    git_dir.mkdir()
    objects_dir.mkdir()

    file = tmp_path / "test.txt"
    content = b"Hello from test_add"
    file.write_bytes(content)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = runner.invoke(app, ["add", str(file.name)])
        assert result.exit_code == 0, f"Error: {result.stderr}"

        header = f"blob {len(content)}\0".encode()
        full_data = header + content

        expected_oid = hashlib.sha1(full_data).hexdigest()
        obj_path = git_dir / "objects" / expected_oid[:2] / expected_oid[2:]
        assert obj_path.exists(), " Object was not created"

        index_path = git_dir / "index.json"
        assert index_path.exists(), " index.json file is missing"

        with open(index_path) as f:
            index = json.load(f)

        assert len(index) == 1, " Index does not contain exactly 1 entry"
        entry = index[0]
        assert entry["mode"] == "100644", " Incorrect mode"
        assert entry["oid"] == expected_oid, " Incorrect OID"
        assert entry["path"] == "test.txt", " Incorrect path"

    finally:
        os.chdir(old_cwd)
