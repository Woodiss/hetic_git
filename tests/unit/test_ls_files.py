
import json
from typer.testing import CliRunner
from git_scratch.main import app


runner = CliRunner()

def test_ls_files(monkeypatch, tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    index_path = git_dir / "index.json"

    entries = [
        {"path": "file1.txt", "mode": "100644", "oid": "abc123"},
        {"path": "src/main.py", "mode": "100644", "oid": "def456"},
    ]

    index_path.write_text(json.dumps(entries))
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["ls-files"])

    assert result.exit_code == 0
    assert "file1.txt" in result.output
    assert "src/main.py" in result.output

