import os
import zlib
from pathlib import Path
import json
from typer.testing import CliRunner
from git_scratch.main import app 

runner = CliRunner()

def test_commit_tree_creates_valid_commit_object(tmp_path, monkeypatch):
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        monkeypatch.setenv("GIT_AUTHOR_NAME", "Alice Dev")
        monkeypatch.setenv("GIT_AUTHOR_EMAIL", "alice@example.com")


        result_init = runner.invoke(app, ["init"])
        assert result_init.exit_code == 0

        # -- Créer un fichier et le hasher avec pit
        file = tmp_path / "hello.txt"
        file.write_text("Salut du test\n")
        result_hash = runner.invoke(app, ["hash-object", str(file), "--write"])
        assert result_hash.exit_code == 0
        blob_oid = result_hash.stdout.strip()

        # -- Créer un index.json minimal
        index = [{
            "path": "hello.txt",
            "oid": blob_oid,
            "mode": "100644"
        }]
        index_path = tmp_path / ".git" / "index.json"
        # Utiliser json.dumps pour une conversion robuste en JSON
        index_path.write_text(json.dumps(index))


        result_tree = runner.invoke(app, ["write-tree"])
        assert result_tree.exit_code == 0
        tree_oid = result_tree.stdout.strip()
        if "Tree OID: " in tree_oid:
            tree_oid = tree_oid.split("Tree OID: ")[1]


        message = "Premier commit pit"
        result_commit = runner.invoke(app, ["commit-tree", tree_oid, "-m", message])
        assert result_commit.exit_code == 0
        commit_oid = result_commit.stdout.strip()


        obj_dir = tmp_path / ".git" / "objects" / commit_oid[:2]
        obj_file = obj_dir / commit_oid[2:]
        assert obj_file.exists(), f"Commit object {commit_oid} not written"

        # -- Décompresser et VÉRIFIER LE CONTENU DU COMMIT (en ignorant l'en-tête)
        with open(obj_file, "rb") as f:
            decompressed_full_content = zlib.decompress(f.read()).decode()

        # Trouver la fin de l'en-tête (le premier caractère nul '\x00')
        null_byte_index = decompressed_full_content.find('\x00')
        assert null_byte_index != -1, "Could not find null byte separator in decompressed content"
        
        # Le contenu "pur" du commit commence après le caractère nul
        commit_body = decompressed_full_content[null_byte_index + 1:]

        # --- Assertions sur le corps du commit ---
        # Remplacez content par commit_body dans vos assertions
        assert commit_body.startswith("tree " + tree_oid), \
            f"Expected commit body to start with 'tree {tree_oid}', but got: '{commit_body[:50]}...'"
        assert f"author Alice Dev <alice@example.com>" in commit_body
        assert f"committer Alice Dev <alice@example.com>" in commit_body
        assert message in commit_body

    finally:
        os.chdir(original_cwd) 