from pathlib import Path
from typing import Optional


class GitError(Exception):
    """Base exception for Git errors."""


class InvalidHeadError(GitError):
    """Raised when HEAD points to an invalid ref or commit, or refers to a missing or invalid object."""


def _is_valid_oid(oid: str) -> bool:
    return len(oid) == 40 and all(c in "0123456789abcdef" for c in oid.lower())


def get_head_commit_oid() -> Optional[str]:
    head_path = Path(".git") / "HEAD"
    if not head_path.exists():
        return None

    head_content = head_path.read_text().strip()

    if head_content.startswith("ref: "):
        ref_name = head_content[len("ref: "):]
        ref_path = Path(".git") / ref_name
        
        if not ref_path.exists():
            return None 

        ref_oid = ref_path.read_text().strip()
        
        if not _is_valid_oid(ref_oid):
            raise InvalidHeadError(f"Ref '{ref_name}' contains an invalid or empty OID: '{ref_oid}'")
        
        return ref_oid
    else:
        if _is_valid_oid(head_content):
            return head_content
        raise InvalidHeadError("HEAD contains an invalid commit OID format.")


def update_head_to_commit(new_commit_oid: str):
    head_path = Path(".git") / "HEAD"

    if not head_path.exists() or not head_path.read_text().strip().startswith("ref: "):
        default_branch = "main"
        branch_ref_path = Path(".git") / "refs" / "heads" / default_branch
        
        branch_ref_path.parent.mkdir(parents=True, exist_ok=True)
        
        branch_ref_path.write_text(new_commit_oid + "\n")
        
        head_path.write_text(f"ref: refs/heads/{default_branch}\n")
        return

    head_content = head_path.read_text().strip()
    ref_name = head_content[len("ref: "):]
    ref_path = Path(".git") / ref_name
    
    ref_path.parent.mkdir(parents=True, exist_ok=True) 
    
    ref_path.write_text(new_commit_oid + "\n")

def get_head_display(oid: str) -> str:
    """
Returns a description of the HEAD for display purposes
    """
    head_path = Path(".git") / "HEAD"
    content = head_path.read_text().strip()

    if content.startswith("ref: "):
        ref = content[len("ref: "):]
        if ref.startswith("refs/heads/"):
            return ref[len("refs/heads/"):]
        return ref
    else:
        return f"HEAD detached at {oid[:7]}"
