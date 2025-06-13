import typer
from git_scratch.commands.hash_object import hash_object
from git_scratch.commands.cat_file import cat_file

app = typer.Typer(help="Git from scratch in Python.")

app.command("hash-object")(hash_object)
app.command("cat-file")(cat_file)


if __name__ == "main":
    app()
