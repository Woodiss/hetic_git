import os
import typer

def rev_parse(
    folder: str = typer.Argument(None, help="Path to the folder where to initialize the repository")
):
    print("Initializing repository...")