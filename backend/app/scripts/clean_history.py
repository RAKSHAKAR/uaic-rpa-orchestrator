"""Enterprise Data Cleanup, Retention & Reconciliation CLI Engine.

Supports multi-category selection, dynamic time-based scoping (Current Month,
Previous Month, N Days/Weeks/Months, Custom Ranges), dry-run calculation,
transactional deletion, and post-cleanup reconciliation.
"""

import argparse
import asyncio
import os
import sys

# Ensure backend root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import redis

from app.core.config import settings
from app.schemas.settings import get_default_extension_dir
from app.services.cleanup_service import (
    CATEGORY_DEFINITIONS,
    calculate_cleanup_preview,
    execute_enterprise_cleanup,
)
from app.services.settings_service import (
    get_system_settings_async,
    save_system_settings_async,
)


def purge_redis_queues() -> int:
    """Flush all Celery and task queues in Redis (backwards-compatibility helper)."""
    try:
        r = redis.Redis.from_url(
            settings.CELERY_BROKER_URL,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        r.flushdb()
        if settings.CELERY_RESULT_BACKEND:
            r_backend = redis.Redis.from_url(
                settings.CELERY_RESULT_BACKEND,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )
            r_backend.flushdb()
        print("[OK] Purged all Redis broker queues and result backend states.")
        return 1
    except Exception as e:
        print(f"[WARNING] Could not connect to Redis: {e}")
        return 0


async def clear_database_records() -> dict:
    """Clear claim records and operational entities (backwards-compatibility helper)."""
    res = await execute_enterprise_cleanup(
        categories=["claims", "court_cases", "fuzzy_matches", "notifications", "bot_history"],
        time_scope="all_time",
        operator="LEGACY_CLEAN_CALLER",
        dry_run=False,
    )
    return res.records_deleted


MENU_CATEGORIES = [
    ("claims", "Claim & Automation Data (claim_records, batches)"),
    ("queue", "Work Queue Data (pending and in-progress items)"),
    ("court_cases", "Scraped Court Case Data (scraped_court_cases)"),
    ("fuzzy_matches", "Fuzzy Match Data (match_pairs)"),
    ("guidewire_activities", "Guidewire Activity Data (claims with activity_id)"),
    ("notifications", "Outbound Notification Data (all notification records)"),
    ("notification_deliveries", "Notification Delivery History (sent/failed receipts)"),
    ("telemetry", "Execution Telemetry & Audit Logs (audit_logs)"),
    ("bot_history", "Bot / Scraper Execution History (error_screenshots)"),
    ("dashboard_metrics", "Dashboard / Analytics Data (cached metrics & stats)"),
    ("run_history", "Application Run History (celerybeat schedules, run logs)"),
    ("app_logs", "Application Logs (logs/*.log, setup logs)"),
    ("scraper_logs", "Scraper Logs & Browser Artifacts (.tempmediaStorage)"),
    ("temp_caches", "Temporary Files & Build Caches (__pycache__, caches)"),
    ("generated_exports", "Generated Export Files (exports/, test_export.*)"),
    ("redis_runtime", "Redis Runtime & Celery Broker Queues"),
    ("all_operational", "All Operational Data Categories (ALL OF THE ABOVE)"),
    ("all_supported", "All Supported Data Categories (Complete Wipe)"),
]

MENU_TIME_SCOPES = [
    ("current_month", "Current Month (Dynamic: 1st of month 00:00:00 to now)"),
    ("previous_month", "Previous Month (1st to last day of previous calendar month)"),
    ("last_n_days", "Last N Days"),
    ("last_n_weeks", "Last N Weeks"),
    ("last_n_months", "Last N Months"),
    ("last_n_years", "Last N Years"),
    ("custom_range", "Custom Date Range (Start Date -> End Date)"),
    ("before_date", "Before Specific Date (Older than cutoff date)"),
    ("after_date", "After Specific Date (Newer than cutoff date)"),
    ("all_time", "All Time (No Date Filter - Delete all matching records)"),
]


def prompt_category_selection() -> list[str]:
    print("\n" + "=" * 70)
    print("      ENTERPRISE DATA CLEANUP — SELECT DATA CATEGORIES")
    print("=" * 70)
    for idx, (cat_id, cat_desc) in enumerate(MENU_CATEGORIES, 1):
        print(f" [{idx:2d}] {cat_desc}")
    print(" [ A] Select ALL Categories")
    print(" [ N] Select None / Cancel")
    print("=" * 70)

    choice = input("\nEnter category number(s) separated by commas (e.g. 1,3,6,7,8) or 'A': ").strip()
    if not choice or choice.lower() == "n":
        print("Cancelled by user. Exiting.")
        sys.exit(0)

    if choice.lower() in ("a", "all", "17", "18"):
        return ["all_operational"]

    selected = []
    for part in choice.split(","):
        p = part.strip()
        if p.isdigit():
            idx = int(p)
            if 1 <= idx <= len(MENU_CATEGORIES):
                selected.append(MENU_CATEGORIES[idx - 1][0])
        elif p in CATEGORY_DEFINITIONS:
            selected.append(p)

    if not selected:
        print("No valid categories selected. Defaulting to all_operational.")
        selected = ["all_operational"]
    return selected


def prompt_time_scope_selection() -> tuple[str, int | None, str | None, str | None, str | None, str | None]:
    print("\n" + "=" * 70)
    print("      ENTERPRISE DATA CLEANUP — SELECT TIME SCOPE")
    print("=" * 70)
    for idx, (scope_id, scope_desc) in enumerate(MENU_TIME_SCOPES, 1):
        print(f" [{idx:2d}] {scope_desc}")
    print("=" * 70)

    choice = input("\nEnter time scope [1-10] (Default: 1 - Current Month): ").strip()
    idx = 1
    if choice.isdigit() and 1 <= int(choice) <= len(MENU_TIME_SCOPES):
        idx = int(choice)

    scope_id = MENU_TIME_SCOPES[idx - 1][0]
    n_units = None
    start_date = None
    end_date = None
    before_date = None
    after_date = None

    if scope_id in ("last_n_days", "last_n_weeks", "last_n_months", "last_n_years"):
        unit_name = scope_id.split("_")[-1]
        val = input(f"Enter number of {unit_name} (e.g. 30): ").strip()
        n_units = int(val) if val.isdigit() else 30
    elif scope_id == "custom_range":
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date   (YYYY-MM-DD): ").strip()
    elif scope_id == "before_date":
        before_date = input("Enter cutoff date (YYYY-MM-DD): ").strip()
    elif scope_id == "after_date":
        after_date = input("Enter cutoff date (YYYY-MM-DD): ").strip()

    return scope_id, n_units, start_date, end_date, before_date, after_date


async def run_interactive_cleanup():
    print("\n" + "=" * 70)
    print("          UAIC ORCHESTRATOR — ENTERPRISE CLEANUP ENGINE")
    print("=" * 70)

    # 1. Categories
    categories = prompt_category_selection()

    # 2. Time Scope
    scope_id, n_units, start_date, end_date, before_date, after_date = prompt_time_scope_selection()

    # 3. Dry-Run Preview
    print("\n[INFO] Calculating affected records and files (Dry-Run Preview)...")
    preview = await calculate_cleanup_preview(
        categories=categories,
        time_scope=scope_id,
        n_units=n_units,
        start_date=start_date,
        end_date=end_date,
        before_date=before_date,
        after_date=after_date,
    )

    print("\n" + "=" * 70)
    print("                     CLEANUP DRY-RUN PREVIEW")
    print("=" * 70)
    print(f"Time Range: {preview.time_scope}")
    print(f"Categories: {', '.join(preview.categories)}")
    print("-" * 70)
    print("AFFECTED DATABASE RECORDS:")
    for cat_name, count in preview.record_counts.items():
        print(f"  {cat_name:<30}: {count:>8,d}")
    print(f"  {'TOTAL DATABASE RECORDS':<30}: {preview.total_database_records:>8,d}")

    if preview.file_counts:
        print("-" * 70)
        print("AFFECTED DISK FILES:")
        for fcat, fcount in preview.file_counts.items():
            print(f"  {fcat:<30}: {fcount:>8,d}")
        print(f"  {'TOTAL DISK FILES':<30}: {preview.total_files:>8,d}")

    print("=" * 70)
    print("WARNING: This operation will permanently delete the selected data.")
    confirm = input("Continue with permanent deletion? [Y/N] (Default: N): ").strip().lower()

    if confirm not in ("y", "yes"):
        print("\nCleanup cancelled. No changes were made.")
        return

    # 4. Execute
    print("\n[INFO] Executing enterprise cleanup inside database transaction...")
    res = await execute_enterprise_cleanup(
        categories=categories,
        time_scope=scope_id,
        n_units=n_units,
        start_date=start_date,
        end_date=end_date,
        before_date=before_date,
        after_date=after_date,
        operator="CONSOLE_OPERATOR",
        dry_run=False,
    )

    # 5. Display Final Report
    print("\n" + "=" * 70)
    print("                       CLEANUP COMPLETED")
    print("=" * 70)
    print(f"Cleanup ID:                           {res.cleanup_id}")
    print(f"Started:                              {res.started_at}")
    print(f"Completed:                            {res.completed_at}")
    print(f"Time Scope:                           {res.time_scope}")
    print("-" * 70)
    print("RECORDS DELETED PER CATEGORY:")
    for cat, dcount in res.records_deleted.items():
        print(f"  {cat:<34}: {dcount:>8,d}")
    print(f"  {'TOTAL DATABASE RECORDS DELETED':<34}: {res.total_records_deleted:>8,d}")
    print(f"  {'TOTAL DISK FILES DELETED':<34}: {res.files_deleted:>8,d}")
    print(f"  {'REDIS QUEUES PURGED':<34}: {'YES' if res.redis_purged else 'NO'}")
    print("-" * 70)
    print(f"Referential Integrity:                {res.referential_integrity}")
    print(f"Dashboard Reconciliation:             {res.dashboard_reconciliation}")
    print(f"Notification History Reconciliation:  {res.notification_history_reconciliation}")
    print(f"Overall Status:                       {'SUCCESS' if res.success else 'FAILED'}")
    print("=" * 70)

    # Ensure system settings remain valid
    try:
        current = await get_system_settings_async()
        ext_p = (current.automation.chrome_extension_dir or "").strip().strip('"').strip("'")
        if not ext_p or not os.path.exists(ext_p):
            current.automation.chrome_extension_dir = get_default_extension_dir()
        current.automation.chrome_user_data_dir = ""
        await save_system_settings_async(current)
    except Exception:
        pass


async def main():
    parser = argparse.ArgumentParser(description="UAIC Orchestrator Enterprise Data Retention & Cleanup")
    parser.add_argument("--categories", type=str, default=None, help="Comma-separated categories or 'all_operational'")
    parser.add_argument("--time-scope", type=str, default=None, help="Time scope (current_month, previous_month, last_n_days, etc.)")
    parser.add_argument("--n-units", type=int, default=None, help="Units for last_n_days, last_n_weeks, etc.")
    parser.add_argument("--start-date", type=str, default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--before-date", type=str, default=None, help="Cutoff date before")
    parser.add_argument("--after-date", type=str, default=None, help="Cutoff date after")
    parser.add_argument("--dry-run", action="store_true", help="Calculate preview without deleting")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    # If any CLI flags provided, run non-interactively
    if args.categories or args.time_scope or args.dry_run:
        cats = [args.categories] if args.categories else ["all_operational"]
        scope = args.time_scope or "current_month"
        if args.dry_run:
            preview = await calculate_cleanup_preview(
                categories=cats,
                time_scope=scope,
                n_units=args.n_units,
                start_date=args.start_date,
                end_date=args.end_date,
                before_date=args.before_date,
                after_date=args.after_date,
            )
            print(f"[PREVIEW] Total DB: {preview.total_database_records}, Files: {preview.total_files}")
            for k, v in preview.record_counts.items():
                print(f"  {k}: {v}")
            return

        res = await execute_enterprise_cleanup(
            categories=cats,
            time_scope=scope,
            n_units=args.n_units,
            start_date=args.start_date,
            end_date=args.end_date,
            before_date=args.before_date,
            after_date=args.after_date,
            operator="CLI_AUTOMATION",
            dry_run=False,
        )
        print(f"[SUCCESS] Cleanup {res.cleanup_id}: Deleted {res.total_records_deleted} DB records, {res.files_deleted} files.")
        for k, v in res.records_deleted.items():
            print(f"  {k}: {v}")
        return

    # Otherwise interactive
    await run_interactive_cleanup()


if __name__ == "__main__":
    asyncio.run(main())
