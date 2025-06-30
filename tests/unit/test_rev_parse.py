import pathlib
import subprocess
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()


def test_rev_parse_head_and_abbrev(tmp_path: pathlib.Path, monkeypatch):
    repo = tmp_path

    # Prépare un dépôt Git minimal
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Pytest"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "pytest@example.com"], cwd=repo, check=True
    )

    (repo / "file.txt").write_text("hello\n")
    subprocess.run(["git", "add", "file.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

    # SHA complet de HEAD
    expected_sha_head = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().lower()
    )

    # Test rev-parse HEAD
    monkeypatch.chdir(repo)
    result_full = runner.invoke(app, ["rev-parse", "HEAD"])
    assert result_full.exit_code == 0, result_full.output
    assert result_full.stdout.strip().lower() == expected_sha_head

    # Test rev-parse abbre sha
    abbrev5 = expected_sha_head[:5]
    result_short = runner.invoke(app, ["rev-parse", abbrev5])
    assert result_short.exit_code == 0, result_short.output
    assert result_short.stdout.strip().lower() == expected_sha_head
