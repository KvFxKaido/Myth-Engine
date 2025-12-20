from __future__ import annotations

import sys
from collections import deque
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def _read_top_level(requirements_in: Path) -> list[str]:
    names: list[str] = []
    for raw in requirements_in.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # allow simple "pkg==x" lines if someone edits by hand
        req = Requirement(line)
        names.append(canonicalize_name(req.name))
    return names


def _iter_deps(dist_name: str) -> list[str]:
    try:
        dist = metadata.distribution(dist_name)
    except metadata.PackageNotFoundError:
        return []

    reqs = dist.requires or []
    out: list[str] = []
    for r in reqs:
        try:
            req = Requirement(r)
        except Exception:
            continue
        if req.marker and not req.marker.evaluate():
            continue
        out.append(canonicalize_name(req.name))
    return out


def _get_version(dist_name: str) -> str | None:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return None


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    requirements_in = repo_root / "Sovwren" / "requirements.in"
    out_path = None
    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1])

    top = _read_top_level(requirements_in)
    queue = deque(top)
    seen: set[str] = set()

    missing: list[str] = []
    while queue:
        name = queue.popleft()
        if name in seen:
            continue
        seen.add(name)

        version = _get_version(name)
        if version is None:
            missing.append(name)
            continue

        for dep in _iter_deps(name):
            if dep not in seen:
                queue.append(dep)

    if missing:
        sys.stderr.write("Missing packages (install first):\n")
        for m in sorted(missing):
            sys.stderr.write(f"  - {m}\n")
        return 2

    lines: list[str] = []
    lines.append("# This file is generated. Do not edit by hand.")
    lines.append("# Regenerate: python Sovwren/tools/generate_requirements_lock.py > Sovwren/requirements.lock")
    lines.append("")

    for name in sorted(seen):
        version = _get_version(name)
        if version is None:
            continue
        # Prefer the canonical name spelling from dist metadata (pip doesn't care).
        dist = metadata.distribution(name)
        display_name = dist.metadata.get("Name", name)
        lines.append(f"{display_name}=={version}")

    content = "\n".join(lines) + "\n"
    if out_path:
        out_path.write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
