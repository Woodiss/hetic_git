import typer
from git_scratch.commands.ls_files import ls_files
from git_scratch.commands.hash_object import hash_object
from git_scratch.commands.cat_file import cat_file
from git_scratch.commands.show_ref import show_ref
from git_scratch.commands.add import add
from git_scratch.commands.write_tree import write_tree
from git_scratch.commands.rmfile import rmfile
from git_scratch.commands.rev_parse import rev_parse
from git_scratch.commands.ls_tree import ls_tree
from git_scratch.commands.status import status

from git_scratch.commands.init import init

app = typer.Typer(help="Git from scratch in Python.")

app.command("hash-object")(hash_object)
app.command("cat-file")(cat_file)
app.command("add")(add)
app.command("write-tree")(write_tree)
app.command("rm")(rmfile)
app.command("init")(init)
app.command("ls-files")(ls_files)
app.command("rev-parse")(rev_parse)
app.command("show-ref")(show_ref)
app.command("ls-tree")(ls_tree)
app.command("status")(status)


if __name__ == "__main__":
    app()
