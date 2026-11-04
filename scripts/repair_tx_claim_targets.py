#!/usr/bin/env python3
"""
Claim Target Column Repair Script — IMP-2026-1007-004 (Phase 2 / GAP-B)

Audits and repairs the te_website_travis and te_website_dallas target columns
for all existing TX-eligible and Cross-State claims that were ingested before
the G-1 fix (when dallas_enabled=False / travis_enabled=False).

Usage:
    cd backend
    .venv/Scripts/python.exe ../scripts/repair_tx_claim_targets.py [--dry-run]

Options:
    --dry-run   Print what would be changed without making any DB changes.
    --fix       Apply the repair (required to actually modify the DB).
"""

import argparse
import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
DB_PATH = BACKEND_DIR / "orchestrator.db"


def normalize_state(s: str | None) -> str:
    if not s:
        return ""
    s = s.strip().upper()
    if s in ("FL", "FLORIDA"):
        return "FL"
    if s in ("TX", "TEXAS"):
        return "TX"
    return s


def run_audit_and_repair(dry_run: bool = True) -> None:
    print(f"\n{'[DRY RUN] ' if dry_run else '[LIVE REPAIR] '}UAIC Claim Target Column Repair")
    print(f"Database: {DB_PATH}\n")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── 1. TX Same-State Claims ───────────────────────────────────────────────
    cur.execute(
        "SELECT id, claim_number, policy_state, loss_location_state, "
        "te_website_travis, te_website_dallas, record_status "
        "FROM claim_records "
        "WHERE UPPER(TRIM(policy_state)) IN ('TX','TEXAS')"
    )
    tx_claims = cur.fetchall()
    print(f"Found {len(tx_claims)} TX same-state claims.")

    tx_to_fix = [
        r for r in tx_claims
        if r["te_website_travis"] != "Yes" or r["te_website_dallas"] != "Yes"
    ]
    print(f"TX claims needing target column repair: {len(tx_to_fix)}")

    for row in tx_to_fix:
        print(
            f"  REPAIR TX Claim {row['claim_number']} "
            f"(travis={row['te_website_travis']}, dallas={row['te_website_dallas']}) "
            f"status={row['record_status']}"
        )
        if not dry_run:
            cur.execute(
                "UPDATE claim_records SET te_website_travis='Yes', te_website_dallas='Yes' "
                "WHERE id=?",
                (row["id"],),
            )

    # ── 2. Cross-State Claims ─────────────────────────────────────────────────
    cur.execute(
        "SELECT id, claim_number, policy_state, loss_location_state, "
        "fl_website_broward, fl_website_hillsborough, fl_website_miami, "
        "te_website_travis, te_website_dallas, te_website_harris, "
        "te_website_cclerk, te_website_hcdistrict, record_status "
        "FROM claim_records "
        "WHERE policy_state IS NOT NULL AND loss_location_state IS NOT NULL "
        "AND TRIM(policy_state) != '' AND TRIM(loss_location_state) != ''"
    )
    all_claims = cur.fetchall()

    cross_claims = [
        r for r in all_claims
        if normalize_state(r["policy_state"]) != normalize_state(r["loss_location_state"])
        and normalize_state(r["policy_state"]) != ""
        and normalize_state(r["loss_location_state"]) != ""
    ]
    print(f"\nFound {len(cross_claims)} cross-state claims.")

    cross_to_fix = [
        r for r in cross_claims
        if any(
            r[col] != "Yes"
            for col in [
                "fl_website_broward", "fl_website_hillsborough", "fl_website_miami",
                "te_website_travis", "te_website_dallas", "te_website_harris",
                "te_website_cclerk", "te_website_hcdistrict",
            ]
        )
    ]
    print(f"Cross-state claims needing target column repair: {len(cross_to_fix)}")

    for row in cross_to_fix:
        bad_cols = [
            col for col in [
                "fl_website_broward", "fl_website_hillsborough", "fl_website_miami",
                "te_website_travis", "te_website_dallas", "te_website_harris",
                "te_website_cclerk", "te_website_hcdistrict",
            ]
            if row[col] != "Yes"
        ]
        print(
            f"  REPAIR CROSS-STATE Claim {row['claim_number']} "
            f"({row['policy_state']}/{row['loss_location_state']}) "
            f"bad_cols={bad_cols} status={row['record_status']}"
        )
        if not dry_run:
            cur.execute(
                "UPDATE claim_records SET "
                "fl_website_broward='Yes', fl_website_hillsborough='Yes', fl_website_miami='Yes', "
                "te_website_travis='Yes', te_website_dallas='Yes', te_website_harris='Yes', "
                "te_website_cclerk='Yes', te_website_hcdistrict='Yes' "
                "WHERE id=?",
                (row["id"],),
            )

    # ── 3. Commit ─────────────────────────────────────────────────────────────
    if not dry_run:
        conn.commit()
        print(f"\n✅ Repair committed: {len(tx_to_fix)} TX + {len(cross_to_fix)} cross-state claims updated.")
    else:
        print(f"\n[DRY RUN] Would repair: {len(tx_to_fix)} TX + {len(cross_to_fix)} cross-state claims.")
        print("Run with --fix to apply changes.")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair TX/Cross-State claim target columns")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview changes without modifying DB")
    group.add_argument("--fix", action="store_true", help="Apply the repair to the database")
    args = parser.parse_args()

    run_audit_and_repair(dry_run=not args.fix)
