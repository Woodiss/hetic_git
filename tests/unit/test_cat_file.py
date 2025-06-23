from pathlib import Path
from typer.testing import CliRunner
import subprocess

from git_scratch.main import app

runner = CliRunner()

def test_cat_file_all_modes(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("Hello from test")

    # 🔄 Calcul du hash avec l'application locale (PIT) au lieu de Git
    result_pit_oid = runner.invoke(app, ["hash-object", str(file)])
    oid = result_pit_oid.stdout.strip()

    # Test des deux modes : -p (print content) et -t (type)
    for flag in ["-p", "-t"]:
        result_git = subprocess.run(
            ["git", "cat-file", flag, oid],
            capture_output=True, text=True
        )
        result_pit = runner.invoke(app, ["cat-file", flag, oid])

        print(f"\n[cat-file {flag}]")
        print("GIT:", repr(result_git.stdout))
        print("PIT:", repr(result_pit.stdout))

        assert result_git.stdout.strip() == result_pit.stdout.strip()
