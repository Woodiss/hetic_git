# git_scratch/pit_identity.py
import os
import configparser
from datetime import datetime
from typing import Tuple

def get_author_identity() -> Tuple[str, str]:
    """
    Get author name and email from environment, .gitconfig or fallback.
    Priority: ENV > .gitconfig > defaults
    """
    # Step 1: try ENV
    name = os.getenv("GIT_AUTHOR_NAME") or os.getenv("GIT_COMMITTER_NAME")
    email = os.getenv("GIT_AUTHOR_EMAIL") or os.getenv("GIT_COMMITTER_EMAIL")

    # Step 2: try .gitconfig
    if not name or not email:
        config = configparser.ConfigParser()
        paths = [
            os.path.expanduser("~/.gitconfig"),                  # global config
            os.path.join(os.getcwd(), ".git", "config")          # project-level config
        ]
        for path in paths:
            if os.path.exists(path):
                config.read(path)
                if config.has_section("user"):
                    name = name or config.get("user", "name", fallback=None)
                    email = email or config.get("user", "email", fallback=None)

    # Step 3: fallback
    name = name or "John Doe"
    email = email or "john@example.com"

    return name, email


def get_timestamp_info() -> Tuple[int, str]:
    now = datetime.now().astimezone()
    timestamp = int(now.timestamp())
    timezone = now.strftime('%z')
    return timestamp, timezone
