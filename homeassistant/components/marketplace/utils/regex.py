"""Regex utils."""

import re

RE_REPOSITORY = re.compile(
    r"(?:(?:.*github.com.)|^)([A-Za-z0-9-]+\/[\w.-]+?)(?:(?:\.git)?|(?:[^\w.-].*)?)$"
)


def extract_repository_from_url(url: str) -> str | None:
    """Extract the owner/repo part form a URL."""
    if not (match := re.match(RE_REPOSITORY, url)):
        return None
    return match.group(1).lower()
