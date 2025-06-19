import typer
from git_scratch.commands.hash_object import hash_object
from git_scratch.commands.cat_file import cat_file
from git_scratch.commands.rmfile import rmfile


app = typer.Typer(help="Git from scratch in Python.")

app.command("hash-object")(hash_object)
app.command("cat-file")(cat_file)
app.command("rm")(rmfile)


if __name__ == "__main__":
    app()
