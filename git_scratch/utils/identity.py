# git_scratch/pit_identity.py
import os
import configparser
from datetime import datetime, timezone
from typing import Tuple
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


def get_timestamp_info(is_committer: bool = False) -> tuple[int, str]:
    """
    Returns the timestamp and timezone for the commit.
    """
    env_date_var = "GIT_COMMITTER_DATE" if is_committer else "GIT_AUTHOR_DATE"
    date_str = os.environ.get(env_date_var)
    
    if date_str:
        parts = date_str.split(' ')
        if len(parts) == 2:
            try:
                timestamp = int(parts[0])
                tz_offset = parts[1]
                if len(tz_offset) == 5 and (tz_offset[0] == '+' or tz_offset[0] == '-'):
                    return timestamp, tz_offset
                print(f"[WARN] Format de fuseau horaire non standard pour '{date_str}'. Tentative d'un autre format.")
            except ValueError:
                print(f"[WARN] Impossible de parser '{parts[0]}' comme un timestamp. Tentative d'un autre format.")
        
        try:
            dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z")
            timestamp = int(dt.timestamp())
            tz_offset = date_str.strip().split()[-1] 
            return timestamp, tz_offset
        except ValueError:
            raise ValueError(f"Format de date/heure invalide dans GIT_AUTHOR_DATE/GIT_COMMITTER_DATE: '{date_str}'. Formats supportés: 'timestamp timezone_offset' ou 'Jour Mois Jour HH:MM:SS Année DécalageTimeZone'.")

    now = datetime.now().astimezone()
    timestamp = int(now.timestamp())
    tz_offset = now.strftime("%z")  # e.g. +0200
    return timestamp, tz_offset