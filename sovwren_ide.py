#!/usr/bin/env python3
"""
Convenience launcher for running Sovwren IDE from the repo root.

This forwards execution to `Sovwren/sovwren_ide.py`.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    sys.dont_write_bytecode = True
    repo_root = Path(__file__).resolve().parent
    target = repo_root / "Sovwren" / "sovwren_ide.py"
    if not target.exists():
        raise SystemExit(f"Cannot find Sovwren IDE entrypoint at: {target}")
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
