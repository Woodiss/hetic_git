import typer

from git_scratch.utils.tree import create_root_tree_object
from git_scratch.utils.commit import build_commit_object
from git_scratch.utils.refs import get_head_commit_oid, update_head_to_commit, get_head_display, InvalidHeadError

def commit(
    message: str = typer.Option(..., "-m", help="The commit message."),
    verbose: bool = typer.Option(True, "--verbose/--quiet", help="Show commit summary."),
):
    """
    Records changes to the repository.
    """
    try:
        tree_oid = create_root_tree_object()
        parent_oid = get_head_commit_oid()

        is_root_commit = parent_oid is None

        new_commit_oid = build_commit_object(
            tree_oid=tree_oid,
            message=message,
            parent_oid=parent_oid
        )

        update_head_to_commit(new_commit_oid)

        if verbose:
            head_desc = get_head_display(new_commit_oid)

            commit_prefix = f"[{head_desc}"
            if is_root_commit:
                commit_prefix += " (root-commit)"
            commit_prefix += f" {new_commit_oid[:7]}]"

            typer.echo(f"{commit_prefix} {message}")
        else:
            typer.echo(new_commit_oid)


    except InvalidHeadError as e:
        typer.secho(f"HEAD Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        if "identity" in str(e).lower():
            typer.secho('\nTo configure your user identity:\n'
                        '  git config --global user.email "you@example.com"\n'
                        '  git config --global user.name "Your Name"\n'
                        "Omit --global to set identity only for this repository.",
                        fg=typer.colors.RED)
        raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
