"""Shared helpers for commit-msg hooks in this directory."""

from __future__ import annotations


def strip_comments(text: str) -> str:
    """Drop lines starting with `#` (git's commit-message comment convention).

    Args:
        text: Raw commit message file contents.

    Returns:
        The message with comment lines removed.
    """
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
