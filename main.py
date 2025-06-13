import typer
from commands.hash_object import app as hash_object_app
from commands.cat_file import cat_file

app = typer.Typer(help="Git from scratch in Python.")
app.add_typer(hash_object_app, name="hash-object")

app.command("cat-file")(cat_file)


if __name__ == "__main__":
    app()

