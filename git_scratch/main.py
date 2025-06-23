import typer
from git_scratch.commands.ls_files import ls_files
from git_scratch.commands.hash_object import hash_object
from git_scratch.commands.cat_file import cat_file
from git_scratch.commands.init import init

app = typer.Typer(help="Git from scratch in Python.")

app.command("hash-object")(hash_object)
app.command("cat-file")(cat_file)
app.command("init")(init)
app.command("ls-files")(ls_files)


if __name__ == "main":
    app()
