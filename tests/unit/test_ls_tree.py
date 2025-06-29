from typer.testing import CliRunner
from git_scratch.main import app
import subprocess
import os
runner = CliRunner()


def make_tree_entry(mode: str, name: str, oid_hex: str) -> bytes:
    """
    Construct a correct binary entry for a Git object of type "tree".
    """
    mode_bytes = mode.encode()
    name_bytes = name.encode()
    oid_bytes = bytes.fromhex(oid_hex)
    return mode_bytes + b" " + name_bytes + b"\x00" + oid_bytes


def test_ls_tree_valid(monkeypatch):
    def mock_read_object(oid):
        assert oid == "abc123"
        entry = make_tree_entry("100644", "file.txt", "0123456789abcdef0123456789abcdef01234567")
        return "tree", entry

    monkeypatch.setattr("git_scratch.commands.ls_tree.read_object", mock_read_object)

    result = runner.invoke(app, ["ls-tree", "abc123"])
    assert result.exit_code == 0

    expected_output = "100644 blob 0123456789abcdef0123456789abcdef01234567\tfile.txt"
    assert expected_output in result.output


def test_ls_tree_matches_git(tmp_path):
    # Crée un dépôt git temporaire
    repo = tmp_path
    os.chdir(repo)
    subprocess.run(["git", "init"], check=True)

    # Ajoute un fichier et crée un commit
    file_path = repo / "file.txt"
    file_path.write_text("Hello, Git!\n")
    subprocess.run(["git", "add", "file.txt"], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

    # Récupère l'OID de l'arbre racine HEAD avec Git
    tree_oid = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"]).decode().strip()

    # Exécute la commande git ls-tree
    git_output = subprocess.check_output(["git", "ls-tree", tree_oid]).decode().strip()

    # Exécute ta commande personnalisée
    result = runner.invoke(app, ["ls-tree", tree_oid])
    pit_output = result.output.strip()

    # Affiche les deux résultats en cas d’échec
    assert result.exit_code == 0, f"pit command failed: {result.output}"
    assert pit_output == git_output, f"\nExpected:\n{git_output}\n\nGot:\n{pit_output}"
