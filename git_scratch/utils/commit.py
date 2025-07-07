from typing import Optional
from git_scratch.utils.identity import get_author_identity, get_timestamp_info
from git_scratch.utils.object import write_object


def build_commit_object(
    tree_oid: str,
    message: str,
    parent_oid: Optional[str] = None,
) -> str:
    """
    Construct and store a commit object.

    Args:
        tree_oid (str): OID of the associated tree.
        message (str): Commit message.
        parent_oid (Optional[str]): Parent commit OID, if any.

    Returns:
        str: The OID of the created commit object.
    """
    author_name, author_email = get_author_identity()
    timestamp, timezone = get_timestamp_info()

    lines = [f"tree {tree_oid}"]

    if parent_oid:
        lines.append(f"parent {parent_oid}")

    lines.append(f"author {author_name} <{author_email}> {timestamp} {timezone}")
    lines.append(f"committer {author_name} <{author_email}> {timestamp} {timezone}")
    lines.append("")
    lines.append(message)

    commit_content = "\n".join(lines).encode()
    oid = write_object(commit_content, "commit")

    return oid
