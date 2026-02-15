"""Check for kadiya updates via GitHub Releases API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
from packaging.version import parse as parse_version

from kadiya import __version__

GITHUB_REPO = "thaaaru/kadiya"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASE_PAGE = f"https://github.com/{GITHUB_REPO}/releases"
TIMEOUT = 5  # seconds


@dataclass
class UpdateResult:
    update_available: bool
    current_version: str
    latest_version: str | None = None
    release_url: str | None = None


async def check_for_updates() -> UpdateResult | None:
    """Check GitHub for a newer kadiya release.

    Returns an UpdateResult if the check succeeds, or None on any failure.
    Never raises — update checking is best-effort.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(
                RELEASES_URL,
                headers={"Accept": "application/vnd.github+json"},
            )
            resp.raise_for_status()

        data = resp.json()
        tag = data.get("tag_name", "")
        # Strip leading 'v' if present (e.g. "v0.2.0" -> "0.2.0")
        latest = tag.lstrip("v")

        if not latest:
            return None

        current = parse_version(__version__)
        remote = parse_version(latest)

        return UpdateResult(
            update_available=remote > current,
            current_version=__version__,
            latest_version=latest,
            release_url=data.get("html_url", RELEASE_PAGE),
        )
    except Exception:
        return None


def check_for_updates_sync() -> UpdateResult | None:
    """Synchronous wrapper for check_for_updates()."""
    try:
        return asyncio.run(check_for_updates())
    except Exception:
        return None
