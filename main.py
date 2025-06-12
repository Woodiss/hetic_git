import typer
from commands.hash_object import app as hash_object_app

app = typer.Typer(help="Git from scratch in Python.")
app.add_typer(hash_object_app, name="hash-object")

if __name__ == "__main__":
    app()

