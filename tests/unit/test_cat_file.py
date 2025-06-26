from typer.testing import CliRunner
import subprocess

from git_scratch.main import app

runner = CliRunner()

def test_cat_file_all_modes(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("Hello from test")

    result_pit_oid = runner.invoke(app, ["hash-object", "-w", str(file)])
    oid = result_pit_oid.stdout.strip()

    for flag in ["-p", "-t"]:
        result_git = subprocess.run(
            ["git", "cat-file", flag, oid],
            capture_output=True, text=True
        )
        result_pit = runner.invoke(app, ["cat-file", flag, oid])

        assert result_git.stdout.strip() == result_pit.stdout.strip()
