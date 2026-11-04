"""Standalone Utility: Complete Enterprise Data & System Purge.

Usage:
    python scripts/clean_all_data.py [--all] [--reset-settings] [--force]
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.cleanup_service import execute_complete_purge

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("clean_all_data")


async def main():
    parser = argparse.ArgumentParser(description="Purge all tables, logs, screenshots, uploads, and queues")
    parser.add_argument("--all", action="store_true", default=True, help="Purge all tables and disk files")
    parser.add_argument("--reset-settings", action="store_true", help="Also reset automation settings to defaults")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    if not args.force:
        print("\n" + "=" * 70)
        print("    WARNING: This will permanently purge ALL databases and files!")
        print("=" * 70)
        c = input("Type 'CONFIRM' or 'Y' to proceed: ").strip().lower()
        if c not in ("confirm", "y", "yes"):
            print("Purge cancelled.")
            sys.exit(0)

    logger.info("Executing complete enterprise purge...")
    report = await execute_complete_purge(
        reset_settings_to_default=args.reset_settings,
        operator="STANDALONE_CLEAN_SCRIPT",
    )
    print("\n" + "=" * 70)
    print("                 COMPLETE PURGE REPORT")
    print("=" * 70)
    for k, v in report.items():
        print(f"  {k:<30}: {v}")
    print("=" * 70)
    print("Purge successfully completed.\n")


if __name__ == "__main__":
    asyncio.run(main())
