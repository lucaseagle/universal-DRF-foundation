#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from difflib import unified_diff
from pathlib import Path

SCHEMA_PATH = Path("openapi/schema.yaml")


def _git_show(path: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path.as_posix()}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def _read_worktree(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _normalize(content: str) -> list[str]:
    # Drop commit lines and normalize line endings for fair comparison.
    lines = []
    for line in content.splitlines():
        clean = line.rstrip("\r")
        if clean.lstrip().startswith("commit:"):
            continue
        lines.append(clean)
    return lines


def main() -> int:
    head_content = _git_show(SCHEMA_PATH)
    work_content = _read_worktree(SCHEMA_PATH)

    head_norm = _normalize(head_content)
    work_norm = _normalize(work_content)

    if head_norm == work_norm:
        return 0

    diff = unified_diff(
        head_norm,
        work_norm,
        fromfile="HEAD:openapi/schema.yaml",
        tofile="worktree:openapi/schema.yaml",
        lineterm="",
    )
    print("OpenAPI schema drift detected (excluding commit field).")
    for line in diff:
        print(line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
