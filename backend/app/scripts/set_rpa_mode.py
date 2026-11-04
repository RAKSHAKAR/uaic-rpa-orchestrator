"""Synchronize RPA execution mode to database, Redis settings, and environment files."""

import argparse
import asyncio
import os
import re
import sys

# Ensure backend root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
ROOT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.settings_service import (
    get_system_settings_async,
    save_system_settings_async,
)


def update_env_file(env_path: str, is_unattended: bool) -> None:
    """Synchronize PLAYWRIGHT_HEADLESS in a target .env file if it exists."""
    if not os.path.isfile(env_path):
        return
    headless_str = "true" if is_unattended else "false"
    try:
        with open(env_path, encoding="utf-8") as f:
            content = f.read()
        if re.search(r"PLAYWRIGHT_HEADLESS\s*=\s*\w+", content, re.IGNORECASE):
            new_content = re.sub(
                r"PLAYWRIGHT_HEADLESS\s*=\s*\w+",
                f"PLAYWRIGHT_HEADLESS={headless_str}",
                content,
                flags=re.IGNORECASE,
            )
        else:
            new_content = content.rstrip() + f"\nPLAYWRIGHT_HEADLESS={headless_str}\n"
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"[WARN] Could not update {env_path}: {e}", file=sys.stderr)


async def sync_mode(mode: str) -> None:
    is_unattended = mode.lower() in ("unattended", "true", "u")
    cfg = await get_system_settings_async()
    cfg.automation.headless_mode = is_unattended
    cfg.automation.human_interaction_mode = "unattended" if is_unattended else "attended"
    await save_system_settings_async(cfg)

    # Synchronize both backend/.env and root .env (if present)
    update_env_file(os.path.join(BACKEND_DIR, ".env"), is_unattended)
    update_env_file(os.path.join(ROOT_DIR, ".env"), is_unattended)

    label = "Unattended (headless_mode=True)" if is_unattended else "Attended (headless_mode=False)"
    print(f"[OK] RPA Execution Mode set to {label} - synchronized to SQLite DB, Redis & .env.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize RPA execution mode to DB & Redis")
    parser.add_argument(
        "--mode",
        choices=["Attended", "Unattended", "attended", "unattended"],
        default="Attended",
        help="RPA mode: Attended or Unattended",
    )
    args = parser.parse_args()
    asyncio.run(sync_mode(args.mode))


if __name__ == "__main__":
    main()
