
import subprocess
from git_scratch.main import app
from typer.testing import CliRunner
import zlib
import os

runner = CliRunner()

def test_hash_object_matches_git_and_writes_blob(tmp_path):
    file = tmp_path / "test.txt"
    content = "Hello Git Scratch"
    file.write_text(content)

    # Initialiser un dépôt Git dans tmp_path
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    # 1. Comparaison du hash sans --write
    result_git = subprocess.run(
        ["git", "hash-object", str(file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    hash_git = result_git.stdout.strip()

    # 🔧 On change manuellement le dossier courant
    current_dir = os.getcwd()
    os.chdir(tmp_path)

    try:
        result_pit = runner.invoke(app, ["hash-object", str(file.name)])
        assert result_pit.exit_code == 0
        hash_pit = result_pit.stdout.strip()
        print("Hash Git : ",hash_git, " Hash Pit : ",hash_pit)
        assert hash_pit == hash_git, "Le hash généré par pit ne correspond pas à celui de Git"

        # 2. Avec l’option --write
        result_write = runner.invoke(app, ["hash-object", str(file.name), "--write"])
        assert result_write.exit_code == 0
        hash_written = result_write.stdout.strip()

        obj_dir = tmp_path / ".git" / "objects" / hash_written[:2]
        obj_file = obj_dir / hash_written[2:]
        assert obj_file.exists(), f"Le blob compressé {obj_file} n'a pas été écrit"

        with open(obj_file, "rb") as f:
            compressed_data = f.read()
        full_data = zlib.decompress(compressed_data)

        expected_header = f"blob {len(content)}\0".encode()
        expected_blob = expected_header + content.encode()
        assert full_data == expected_blob, "Le contenu du blob est incorrect"
    
    finally:
        os.chdir(current_dir)  # On revient dans le dossier original à la fin

