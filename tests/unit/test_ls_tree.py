
import pytest
from typer.testing import CliRunner
from git_scratch.main import app

runner = CliRunner()


def make_tree_entry(mode: str, name: str, oid_hex: str) -> bytes:
    mode_bytes = mode.encode()
    name_bytes = name.encode()
    oid_bytes = bytes.fromhex(oid_hex)
    return mode_bytes + b' ' + name_bytes + b'\x00' + oid_bytes


@pytest.fixture
def mock_read_object(monkeypatch):
    def _mock(oid):
        if oid == "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef":
            entry = make_tree_entry("100644", "file.txt", "0123456789abcdef0123456789abcdef01234567")
            return "tree", entry
        raise FileNotFoundError()

    # patch au bon endroit : là où `ls_tree` importe read_object
    monkeypatch.setattr("git_scratch.commands.ls_tree.read_object", _mock)

def test_ls_tree_valid_oid(mock_read_object):
    result = runner.invoke(app, ["ls-tree", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"])
    assert result.exit_code == 0
    assert "100644 0123456789abcdef0123456789abcdef01234567 file.txt" in result.output


def test_ls_tree_oid_not_found(monkeypatch):
    def mock_not_found(oid):
        raise FileNotFoundError()

    monkeypatch.setattr("git_scratch.commands.ls_tree.read_object", mock_not_found)

    result = runner.invoke(app, ["ls-tree", "notfound0000000000000000000000000000000000"])
    assert result.exit_code == 1
    assert "Error: Object notfound0000000000000000000000000000000000 not found." in result.output


def test_ls_tree_oid_wrong_type(monkeypatch):
    def mock_wrong_type(oid):
        return "blob", b"some content"

    monkeypatch.setattr("git_scratch.commands.ls_tree.read_object", mock_wrong_type)

    result = runner.invoke(app, ["ls-tree", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"])
    assert result.exit_code == 1
    assert "Error: Object aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa is not a tree." in result.output

