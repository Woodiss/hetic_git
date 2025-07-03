# git_scratch/pit_identity.py
import os
import configparser
from datetime import datetime
from typing import Tuple
import typer
from pathlib import Path

def get_author_identity() -> Tuple[str, str]:
    """
    Retrieve the author's identity following Git's resolution order:
    1. Environment variables
    2. Repository config (.git/config)
    3. Global config (~/.gitconfig)
    If none found, raise an error similar to Git.
    """
    name = os.getenv("GIT_AUTHOR_NAME") or os.getenv("GIT_COMMITTER_NAME")
    email = os.getenv("GIT_AUTHOR_EMAIL") or os.getenv("GIT_COMMITTER_EMAIL")

    if not name or not email:
        config = configparser.ConfigParser()
        paths = [
            Path(".git") / "config",        # Local project config
            Path.home() / ".gitconfig"      # Global config
        ]
        for path in paths:
            if path.exists():
                try:
                    config.read(path)
                    if config.has_section("user"):
                        name = name or config.get("user", "name", fallback=None)
                        email = email or config.get("user", "email", fallback=None)
                except configparser.Error as e:
                    typer.secho(f"[warn] Failed to parse config at {path}: {e}", fg=typer.colors.YELLOW)

    if not name or not email:
        typer.secho(
            "*** Please tell me who you are.\n\n"
            "Run\n"
            '  git config --global user.email "you@example.com"\n'
            '  git config --global user.name "Your Name"\n\n'
            "to set your account's default identity.\n"
            "Omit --global to set the identity only in this repository.\n",
            fg=typer.colors.RED
        )
        raise typer.Exit(code=1)

    return name, email


def get_timestamp_info() -> Tuple[int, str]:
    now = datetime.now().astimezone()
    timestamp = int(now.timestamp())
    timezone = now.strftime('%z')
    return timestamp, timezone
