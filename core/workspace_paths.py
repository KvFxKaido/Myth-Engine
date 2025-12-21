from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """
    Best-effort repo root detection.

    Prefers a parent containing `.git`. Falls back to the parent of the `Sovwren/`
    package directory if `.git` is not present (e.g., in a release zip).
    """
    start_path = (start or Path(__file__)).resolve()

    for parent in (start_path, *start_path.parents):
        if (parent / ".git").exists():
            return parent

    # workspace_paths.py lives at: <repo>/Sovwren/core/workspace_paths.py
    # -> core -> Sovwren -> <repo>
    try:
        return start_path.parents[2]
    except IndexError:
        return start_path.parent


def find_sovwren_package_root() -> Path:
    """Return the `Sovwren/` package directory (the one containing `config.py`)."""
    return Path(__file__).resolve().parents[1]


def workspace_path(*parts: str) -> Path:
    """Convenience helper for paths under the repo root."""
    return find_repo_root(Path(__file__)) / Path(*parts)

