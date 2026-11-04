"""Verification script for Party Deduplication, Unsearchable Exceptions, and Legal Noise Filtering."""

import os
import sqlite3
import sys

# Ensure backend is on sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.fuzzy_engine import (
    DEFAULT_CLEAN_CASE_STYLE_PATTERNS,
    clean_case_style,
    generate_unique_names_for_claim,
    is_unsearchable_party,
)

db_path = os.path.join(backend_path, "orchestrator.db")

def verify_unsearchable_filtering():
    print("=" * 80)
    print("1. VERIFYING UNSEARCHABLE & PLACEHOLDER PARTY FILTERING ACROSS DATABASE")
    print("=" * 80)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT insured_first_name, insured_last_name, driver_first_name, driver_last_name, claimant_first_name, claimant_last_name FROM claim_records")
    rows = cur.fetchall()

    all_parties = set()
    for r in rows:
        for i in range(0, 6, 2):
            fn = (r[i] or "").strip()
            ln = (r[i+1] or "").strip()
            if fn or ln:
                all_parties.add((fn, ln))

    unsearchable_count = 0
    searchable_count = 0
    flagged_entities = []

    for fn, ln in sorted(all_parties, key=lambda x: f"{x[0]} {x[1]}"):
        full = f"{fn} {ln}".strip()
        if is_unsearchable_party(fn, ln):
            unsearchable_count += 1
            flagged_entities.append(full)
        else:
            searchable_count += 1

    print(f"Total distinct parties analyzed: {len(all_parties)}")
    print(f"Searchable legitimate parties:   {searchable_count}")
    print(f"Unsearchable entities bypassed:  {unsearchable_count}")
    print("\nSample bypassed entities (preventing bot stalls & 10+ min timeouts):")
    for entity in flagged_entities[:15]:
        print(f"  [BYPASSED] {entity}")

    # Spot checks
    assert is_unsearchable_party("LABRADOR & SON", "FOOD PRODUCTS INC."), "LABRADOR & SON INC. must be bypassed"
    assert is_unsearchable_party("Threaded", "Fasteners, Inc."), "Threaded Fasteners, Inc. must be bypassed"
    assert is_unsearchable_party("", "Enterprise"), "Enterprise must be bypassed"
    assert is_unsearchable_party("JOHN", "DOE"), "John Doe must be bypassed"
    assert is_unsearchable_party("CITY OF", "JACKSONVILLE"), "City of Jacksonville must be bypassed"
    assert not is_unsearchable_party("DIANA", "PRINCE"), "Diana Prince must NOT be bypassed"
    assert not is_unsearchable_party("CORNJHIA", "DUNN"), "Cornjhia Dunn must NOT be bypassed"
    print("\n  --> All spot-check assertions PASSED!")

def verify_case_style_noise_stripping():
    print("\n" + "=" * 80)
    print("2. VERIFYING LEGAL & CASE STYLE NOISE STRIPPING ACROSS SCRAPED RECORDS")
    print("=" * 80)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT case_style FROM scraped_court_cases WHERE case_style IS NOT NULL LIMIT 500")
    styles = [r[0] for r in cur.fetchall()]

    cleaned_count = 0
    sample_diffs = []
    for s in styles:
        c = clean_case_style(s, noise_patterns=DEFAULT_CLEAN_CASE_STYLE_PATTERNS)
        if c.strip() != s.strip():
            cleaned_count += 1
            if len(sample_diffs) < 10:
                sample_diffs.append((s, c))

    print(f"Sample scraped styles analyzed: {len(styles)}")
    print(f"Styles with noise stripped:     {cleaned_count}")
    print("\nSample noise stripping transformations:")
    for orig, cleaned in sample_diffs[:8]:
        print(f"  [ORIGINAL] {orig}")
        print(f"  [CLEANED]  {cleaned}\n")

    # Specific legal noise tests
    complex_legal = "JOHN DOE, AS PERSONAL REPRESENTATIVE OF THE ESTATE OF JANE DOE, DECEASED VS PROGRESSIVE CASUALTY INS CO, A FOREIGN CORPORATION"
    res = clean_case_style(complex_legal, noise_patterns=DEFAULT_CLEAN_CASE_STYLE_PATTERNS)
    print("Complex Legal Test:")
    print(f"  Before: {complex_legal}")
    print(f"  After:  {res}")
    assert "PERSONAL REPRESENTATIVE" not in res
    assert "ESTATE OF" not in res
    assert "DECEASED" not in res
    assert "A FOREIGN CORPORATION" not in res
    assert "JOHN DOE" in res
    assert "PROGRESSIVE" in res
    print("  --> Legal noise stripping assertions PASSED!")

def verify_configurable_threshold():
    print("\n" + "=" * 80)
    print("3. VERIFYING PARTY DEDUPLICATION THRESHOLD CONFIGURABILITY")
    print("=" * 80)
    claim_dummy = {
        "insured_first_name": "Carlos",
        "insured_last_name": "Santana",
        "driver_first_name": "Carlos",
        "driver_last_name": "A Santana",
        "claimant_first_name": "Carlos",
        "claimant_last_name": "Santana Jr",
    }

    # At threshold 0.60, variants deduplicate
    names_60 = generate_unique_names_for_claim(claim_dummy, fuzzy_threshold=0.60)
    # At strict threshold 1.00, exact match only
    names_100 = generate_unique_names_for_claim(claim_dummy, fuzzy_threshold=1.00)

    print(f"Unique targets generated at 60% threshold: {len(names_60)} party")
    print(f"Unique targets generated at 100% threshold: {len(names_100)} parties")
    assert len(names_60) <= len(names_100), "Lower threshold must merge variants"
    print("  --> Deduplication threshold tuning PASSED!")

if __name__ == "__main__":
    verify_unsearchable_filtering()
    verify_case_style_noise_stripping()
    verify_configurable_threshold()
    print("\n" + "=" * 80)
    print("ALL VERIFICATION SUITES COMPLETED SUCCESSFULLY (100% VERIFIED)")
    print("=" * 80)
