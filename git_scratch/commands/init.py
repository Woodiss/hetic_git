import os
import typer

app = typer.Typer()

def init():
    """
    Initialize a new, empty pit repository.
    """
    # os.getcwd() = current path
    git_dir = os.path.join(os.getcwd(), ".git")

    if os.path.exists(git_dir):
        typer.secho("Reinitialized existing Pit repository in {}/.git/".format(os.getcwd()), fg=typer.colors.YELLOW)
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
        f.write("ref: refs/heads/main\n")
    with open(os.path.join(git_dir, "config"), "w") as f:
        f.write(
            "[core]\n"
            "\trepositoryformatversion = 0\n"
            "\tfilemode = true\n"
            "\tbare = false\n"
        )
    with open(os.path.join(git_dir, "description"), "w") as f:
        f.write("Unnamed pit repository; edit this file 'description' to name the repository.\n")

    typer.secho("Initialized empty Pit repository in {}/.git/".format(os.getcwd()), fg=typer.colors.GREEN)
