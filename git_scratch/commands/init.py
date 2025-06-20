import os
import typer

app = typer.Typer()

def init(
    folder: str = typer.Argument(None, help="Path to the folder where to initialize the repository")
):
    """
    Initialize a new, empty pit repository.
    """
    # os.getcwd() = current path
    target_dir = os.path.abspath(folder) if folder else os.getcwd()
    git_dir = os.path.join(target_dir, ".git")

    if os.path.exists(git_dir):
        typer.secho("Reinitialized existing Pit repository in {}/.git/".format(target_dir), fg=typer.colors.YELLOW)
        raise typer.Exit()

    # Create basic Git structure
    os.makedirs(os.path.join(git_dir, "objects", "info"), exist_ok=True)
    os.makedirs(os.path.join(git_dir, "objects", "pack"), exist_ok=True)
    os.makedirs(os.path.join(git_dir, "refs", "heads"), exist_ok=True)
    os.makedirs(os.path.join(git_dir, "refs", "tags"), exist_ok=True)
    os.makedirs(os.path.join(git_dir, "hooks"), exist_ok=True)
    os.makedirs(os.path.join(git_dir, "info"), exist_ok=True)

    # Create essential files
    with open(os.path.join(git_dir, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")
    with open(os.path.join(git_dir, "config"), "w") as f:
        f.write(
            "[core]\n"
            "\trepositoryformatversion = 0\n"
            "\tfilemode = true\n"
            "\tbare = false\n"
            "\tlogallrefupdates = true\n"
        )
    with open(os.path.join(git_dir, "description"), "w") as f:
        f.write("Unnamed pit repository; edit this file 'description' to name the repository.\n")

    typer.secho("Initialized empty Pit repository in {}/.git/".format(target_dir), fg=typer.colors.GREEN)
