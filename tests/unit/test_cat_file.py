from pathlib import Path
from typer.testing import CliRunner
import subprocess

from git_scratch.main import app

runner = CliRunner()

def test_cat_file_matches_git(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("Hello from test")

    result_git_oid = subprocess.run(
        ["git", "hash-object", "-w", str(file)],
        capture_output=True, text=True
    )
    oid = result_git_oid.stdout.strip()

    runner.invoke(app, ["hash-object", str(file)])

    result_git_cat = subprocess.run(
        ["git", "cat-file", "-p", oid],
        capture_output=True, text=True
    )
    result_pit_cat = runner.invoke(app, ["cat-file", "-p", oid])

    #  Affichage des résultats pour inspection
    print("\n[cat-file -p]")
    print("GIT:", repr(result_git_cat.stdout))
    print("PIT:", repr(result_pit_cat.stdout))

    assert result_git_cat.stdout.strip() == result_pit_cat.stdout.strip()


def test_cat_file_type_matches_git(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("Hello from test")

    result_git_oid = subprocess.run(
        ["git", "hash-object", "-w", str(file)],
        capture_output=True, text=True
    )
    oid = result_git_oid.stdout.strip()

    runner.invoke(app, ["hash-object", str(file)])

    result_git_type = subprocess.run(
        ["git", "cat-file", "-t", oid],
        capture_output=True, text=True
    )
    result_pit_type = runner.invoke(app, ["cat-file", "-t", oid])

    #  Affichage des résultats pour inspection
    print("\n[cat-file -t]")
    print("git:", repr(result_git_type.stdout))
    print("pit:", repr(result_pit_type.stdout))

    assert result_git_type.stdout.strip() == result_pit_type.stdout.strip()

