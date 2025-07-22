
import subprocess
from typer.testing import CliRunner

# On importe ta commande Typer (par exemple depuis git_scratch.main)
from git_scratch.main import app  # adapte selon où est défini ton Typer app

runner = CliRunner()

def run(cmd, cwd):
    """Helper pour exécuter une commande shell et retourner stdout."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def test_pit_log_matches_git_with_typer(monkeypatch, tmp_path):
    # 1️⃣ Créer un repo temporaire
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    
    # Initialiser un repo Git
    run(["git", "init"], cwd=repo_path)
    
    # Faire quelques commits
    f1 = repo_path / "file1.txt"
    f1.write_text("hello world")
    run(["git", "add", "file1.txt"], cwd=repo_path)
    run(["git", "commit", "-m", "Initial commit"], cwd=repo_path)
    
    f1.write_text("update content")
    run(["git", "add", "file1.txt"], cwd=repo_path)
    run(["git", "commit", "-m", "Second commit"], cwd=repo_path)
    
    f2 = repo_path / "file2.txt"
    f2.write_text("another file")
    run(["git", "add", "file2.txt"], cwd=repo_path)
    run(["git", "commit", "-m", "Third commit"], cwd=repo_path)
    
    # 2️⃣ Récupérer le log git dans un format simple
    git_log = run(["git", "log", "--pretty=format:%H %s"], cwd=repo_path)
    
    # 3️⃣ Monkeypatcher le répertoire courant pour que pit log s’exécute dans repo_path
    monkeypatch.chdir(repo_path)
    
    # 4️⃣ Exécuter `pit log` via Typer Testing
    result = runner.invoke(app, ["log"])
    
    assert result.exit_code == 0, f"pit log failed: {result.output}"
    
    pit_log_output = result.output
    
    # 5️⃣ Comparer les commits git avec ceux affichés par pit
    for line in git_log.splitlines():
        commit_hash, message = line.split(" ", 1)
        # On vérifie que pit log contient bien le hash et le message
        assert commit_hash in pit_log_output
        assert message in pit_log_output
