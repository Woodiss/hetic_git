import typer
from git_scratch.commands.hash_object import hash_object
from git_scratch.commands.cat_file import cat_file
from git_scratch.commands.add import add
from git_scratch.commands.write_tree import write_tree

app = typer.Typer(help="Git from scratch in Python.")

app.command("hash-object")(hash_object)
app.command("cat-file")(cat_file)
app.command("add")(add)
app.command("write-tree")(write_tree)


if __name__ == "main":
    app()
