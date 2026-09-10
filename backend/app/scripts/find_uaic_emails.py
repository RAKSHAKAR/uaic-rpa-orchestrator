"""
find_uaic_emails.py -- UAIC Codebase Email Compliance Scanner
=============================================================
Scans SOURCE CODE for any hardcoded @uaic.com email addresses.

@uaic.com is a fictional test domain that must NEVER appear in production code.
All email addresses must be configurable via SystemSettings or environment variables.

Scans: backend/, frontend/src/, scripts/
Skips: implementation_plan/, PowerAutomateSolutions/, Testing files/, .venv, node_modules

Usage:
    cd backend
    .venv\\Scripts\\python app/scripts/find_uaic_emails.py

Exit codes:
    0 -- Clean: 0 occurrences found in source code
    1 -- Action required: 1 or more occurrences found
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Repository root: three levels up from backend/app/scripts/
#   backend/app/scripts/ -> backend/app/ -> backend/ -> Bot_UAIC/
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Only scan these top-level source directories (relative to REPO_ROOT)
SOURCE_DIRS = ["backend", "frontend/src", "scripts"]

# File extensions to scan within those source directories
SCAN_EXTENSIONS = (".py", ".ts", ".tsx", ".js", ".ps1", ".env", ".example", ".yml", ".yaml", ".json")

# Directories to skip entirely (anywhere in the tree)
SKIP_DIRS = {
    ".venv", "node_modules", ".next", "__pycache__", ".git",
    ".tempmediaStorage", "anticaptcha-plugin_v0.83", ".pytest_cache", ".ruff_cache",
    "implementation_plan", "PowerAutomateSolutions", "Testing files",
}

# Exclude this script and the companion root-level script from matching themselves
EXCLUDED_FILENAMES = {"find_uaic_emails.py"}

# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan_directory(scan_root: str) -> list[tuple[str, int, str]]:
    """Walk *scan_root* and return (rel_path, lineno, line) for every @uaic.com match."""
    hits: list[tuple[str, int, str]] = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname in EXCLUDED_FILENAMES:
                continue
            if not fname.endswith(SCAN_EXTENSIONS):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        if "@uaic.com" in line.lower():
                            rel = os.path.relpath(fpath, REPO_ROOT)
                            hits.append((rel, lineno, line.rstrip()))
            except (PermissionError, OSError):
                pass
    return hits


def safe_print(text: str) -> None:
    """Print text, replacing unencodable characters for Windows cp1252 consoles."""
    sys.stdout.buffer.write((text + "\n").encode(sys.stdout.encoding or "utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    sep = "=" * 65
    safe_print("")
    safe_print(sep)
    safe_print("  UAIC Codebase Email Compliance Scanner")
    safe_print("  Scanning SOURCE CODE for @uaic.com occurrences...")
    safe_print(f"  Root: {REPO_ROOT}")
    safe_print(f"  Scanning: {', '.join(SOURCE_DIRS)}")
    safe_print(sep)

    all_hits: list[tuple[str, int, str]] = []
    for src in SOURCE_DIRS:
        full_src = os.path.join(REPO_ROOT, src)
        if os.path.isdir(full_src):
            all_hits.extend(scan_directory(full_src))

    safe_print("")
    for rel, lineno, line in all_hits:
        safe_print(f"  FOUND  {rel}:{lineno}")
        safe_print(f"         {line}")

    safe_print("")
    safe_print(sep)
    if not all_hits:
        safe_print("  RESULT: 0 occurrences found -- CLEAN [PASS]")
        safe_print("  No @uaic.com addresses exist in source code.")
        safe_print(sep)
        safe_print("")
        return 0
    else:
        safe_print(f"  RESULT: {len(all_hits)} occurrence(s) found -- ACTION REQUIRED [FAIL]")
        safe_print("  Replace all @uaic.com addresses with configurable values.")
        safe_print("  Use SystemSettings or environment variables instead.")
        safe_print(sep)
        safe_print("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
