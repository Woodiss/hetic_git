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

    Raises:
    ValueError: If author name or email cannot be determined.
    
    Returns:
        Tuple[str, str]: The author's name and email.
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
                    print(f"[warn] Failed to parse config at {path}: {e}")

    if not name or not email:
        raise ValueError("Author identity unknown. Please configure it using 'git config'.")

    return name, email


def get_timestamp_info() -> Tuple[int, str]:
    """
    Retrieve the current timestamp and timezone offset in Git's format.
    
    Returns:
        Tuple[int, str]: Timestamp (seconds since epoch) and timezone offset (e.g., "+0100").
    """
    now = datetime.now().astimezone()
    timestamp = int(now.timestamp())
    timezone = now.strftime('%z')
    return timestamp, timezone
