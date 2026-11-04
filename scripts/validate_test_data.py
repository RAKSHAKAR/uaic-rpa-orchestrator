"""Validation script for UAIC 100-Record Cross-State Test Dataset."""

import hashlib
import os
import sys

sys.path.insert(0, os.path.abspath("backend"))

import pandas as pd
from app.services.excel_parser import resolve_county_bot_targets
from app.services.fuzzy_engine import generate_unique_names_for_claim

FILE_PATH = "UAIC_100_RECORD_CROSS_STATE_TEST_DATA.xlsx"


def validate():
    assert os.path.exists(FILE_PATH), f"File {FILE_PATH} does not exist!"

    # Calculate SHA256 Checksum
    with open(FILE_PATH, "rb") as f:
        file_bytes = f.read()
        sha256_checksum = hashlib.sha256(file_bytes).hexdigest()

    df = pd.read_excel(FILE_PATH, sheet_name="CrossState_100Records")

    total_records = len(df)
    assert total_records == 100, f"Expected 100 records, got {total_records}"

    driver_entries = 0
    insured_entries = 0
    claimant_entries = 0
    distinct_user_counts = []
    invalid_records = 0

    expected_portals = [
        "fl_broward",
        "fl_hillsborough",
        "fl_miami",
        "te_travis",
        "te_dallas",
        "te_harris",
        "te_cclerk",
        "te_hcdistrict",
    ]

    for idx, row in df.iterrows():
        # Check claim number
        claim_no = str(row.get("Claim Number") or "").strip()
        if not claim_no.startswith("CLM-2026-XSTATE-"):
            invalid_records += 1

        # Check DOL
        dol = str(row.get("DOL") or "").strip()
        if not dol or len(dol.split("/")) != 3:
            invalid_records += 1

        # Check Cross-State Routing
        pol_st = str(row.get("Policy State") or "").strip()
        loss_st = str(row.get("Loss Location State") or "").strip()
        targets = resolve_county_bot_targets(pol_st, loss_st)
        for p in expected_portals:
            if targets[p] != "Yes":
                invalid_records += 1

        drv_f = str(row.get("Driver First Name") or "").strip()
        drv_l = str(row.get("Driver Last Name") or "").strip()
        ins_f = str(row.get("Insured First Name") or "").strip()
        ins_l = str(row.get("Insured Last Name") or "").strip()
        clm_f = str(row.get("Claimant First Name") or "").strip()
        clm_l = str(row.get("Claimant Last Name") or "").strip()

        if drv_f and drv_l:
            driver_entries += 1
        if ins_f and ins_l:
            insured_entries += 1
        if clm_f and clm_l:
            claimant_entries += 1

        # Check unique names extraction
        unique_targets = generate_unique_names_for_claim(
            {
                "driver_first_name": drv_f,
                "driver_last_name": drv_l,
                "insured_first_name": ins_f,
                "insured_last_name": ins_l,
                "claimant_first_name": clm_f,
                "claimant_last_name": clm_l,
            },
            fuzzy_threshold=0.60,
        )
        distinct_user_counts.append(len(unique_targets))

    total_user_entries = driver_entries + insured_entries + claimant_entries
    distinct_per_record = (
        sum(distinct_user_counts) / len(distinct_user_counts)
        if distinct_user_counts
        else 0
    )

    print("\n" + "=" * 60)
    print("UAIC 100-RECORD CROSS-STATE DATASET VALIDATION REPORT")
    print("=" * 60)
    print(f"File Name:                      {FILE_PATH}")
    print(f"File Size:                      {len(file_bytes):,} bytes")
    print(f"SHA-256 Checksum:               {sha256_checksum}")
    print("-" * 60)
    print(
        f"{'Metric':<35} | {'Expected':>10} | {'Actual':>10} | {'Status':>8}"
    )
    print("-" * 60)

    metrics = [
        ("Total records", 100, total_records),
        ("Driver entries", 100, driver_entries),
        ("Insured entries", 100, insured_entries),
        ("Claimant entries", 100, claimant_entries),
        ("Total individual user entries", 300, total_user_entries),
        ("Distinct users per record", 3, int(distinct_per_record)),
        ("Invalid records", 0, invalid_records),
    ]

    all_passed = True
    for name, exp, act in metrics:
        passed = exp == act
        if not passed:
            all_passed = False
        print(
            f"{name:<35} | {exp:>10} | {act:>10} | {'PASS' if passed else 'FAIL':>8}"
        )

    print("=" * 60)
    print(f"Overall Validation Result:      {'PASS' if all_passed else 'FAIL'}")
    print("=" * 60 + "\n")
    return all_passed


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)

