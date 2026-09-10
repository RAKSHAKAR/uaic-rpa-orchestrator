"""Excel and CSV Claim Ingestion and Validation Service."""

import logging
import math
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

logger = logging.getLogger("uaic_orchestrator.excel_parser")


def convert_excel_date(val: Any) -> str | None:
    """Convert Excel serial date number (based on 1899-12-30 epoch) or string to MM/DD/YYYY."""
    if val is None or pd.isna(val):
        return None
    
    # If already a string
    if isinstance(val, str):
        val_str = val.strip()
        if not val_str or val_str.lower() in ["null", "none", "nan"]:
            return None
        # Try parsing standard formats
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%Y/%m/%d", "%m-%d-%Y", "%d/%m/%Y"]:
            try:
                dt = datetime.strptime(val_str, fmt)
                return dt.strftime("%m/%d/%Y")
            except ValueError:
                pass
        return val_str

    # If datetime/Timestamp
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%m/%d/%Y")

    # If numeric Excel serial date
    if isinstance(val, (int, float)):
        if math.isnan(val):
            return None
        try:
            # Excel epoch starts 1899-12-30
            dt = datetime(1899, 12, 30) + timedelta(days=int(val))
            return dt.strftime("%m/%d/%Y")
        except Exception as e:
            logger.warning(f"Failed to convert Excel serial date {val}: {e}")
            return str(val)

    return str(val)


def resolve_county_bot_targets(policy_state: str | None, loss_state: str | None) -> dict[str, str]:
    """
    Resolve target county RPA bots based on legacy switch routing logic:
    - If Policy State == Loss Location State:
      * Florida -> Broward, Hillsborough, Miami = 'Yes', Texas = 'No'
      * Texas -> Travis, Dallas, Harris, CClerk, Hcdistrict = 'Yes', Florida = 'No'
      * Other -> All 8 = 'Yes'
    - If Policy State != Loss Location State:
      * All 8 = 'Yes'
    """
    targets = {
        "fl_broward": "No",
        "fl_hillsborough": "No",
        "fl_miami": "No",
        "te_travis": "No",
        "te_dallas": "No",
        "te_harris": "No",
        "te_cclerk": "No",
        "te_hcdistrict": "No",
    }

    p_state = (policy_state or "").strip().title()
    l_state = (loss_state or "").strip().title()

    if p_state and l_state and p_state == l_state:
        if p_state in ["Florida", "Fl"]:
            targets["fl_broward"] = "Yes"
            targets["fl_hillsborough"] = "Yes"
            targets["fl_miami"] = "Yes"
        elif p_state in ["Texas", "Tx"]:
            targets["te_travis"] = "Yes"
            targets["te_dallas"] = "Yes"
            targets["te_harris"] = "Yes"
            targets["te_cclerk"] = "Yes"
            targets["te_hcdistrict"] = "Yes"
        else:
            # Default for same-state match
            for k in targets:
                targets[k] = "Yes"
    else:
        # Cross-state or undefined state: trigger all scrapers
        for k in targets:
            targets[k] = "Yes"

    return targets


from rapidfuzz import fuzz

TARGET_CLAIM_FIELDS = [
    {
        "key": "claim_number",
        "label": "Claim Number",
        "required": True,
        "description": "Unique claim identifier (Required)",
        "aliases": [
            "claim number", "claim_number", "claim #", "claim#", "claimno",
            "claim_id", "claim id", "claim", "claimnum", "claim identifier", "claim_no"
        ],
    },
    {
        "key": "insured_first_name",
        "label": "Insured First Name",
        "required": False,
        "description": "First name of insured policyholder",
        "aliases": [
            "insured first name", "insured_first_name", "insured first",
            "ins first", "insured_fname", "insured firstname", "ins_first", "insured_fn"
        ],
    },
    {
        "key": "insured_last_name",
        "label": "Insured Last Name",
        "required": False,
        "description": "Last name of insured policyholder",
        "aliases": [
            "insured last name", "insured_last_name", "insured last",
            "ins last", "insured_lname", "insured lastname", "ins_last", "insured_ln"
        ],
    },
    {
        "key": "claimant_first_name",
        "label": "Claimant First Name",
        "required": False,
        "description": "First name of claiming party",
        "aliases": [
            "claimant first name", "claimant_first_name", "claimant first",
            "clm first", "claimant_fname", "claimant firstname", "clm_first", "claimant_fn"
        ],
    },
    {
        "key": "claimant_last_name",
        "label": "Claimant Last Name",
        "required": False,
        "description": "Last name of claiming party",
        "aliases": [
            "claimant last name", "claimant_last_name", "claimant last",
            "clm last", "claimant_lname", "claimant lastname", "clm_last", "claimant_ln"
        ],
    },
    {
        "key": "driver_first_name",
        "label": "Driver First Name (Insured Vehicle)",
        "required": False,
        "description": "First name of driver of insured vehicle",
        "aliases": [
            "driver first name (insured vehicle)", "driver first name",
            "driver_first_name", "driver first", "drv first", "driver_fname",
            "driver firstname", "drv_first", "driver_fn"
        ],
    },
    {
        "key": "driver_last_name",
        "label": "Driver Last Name (Insured Vehicle)",
        "required": False,
        "description": "Last name of driver of insured vehicle",
        "aliases": [
            "driver last name (insured vehicle)", "driver last name",
            "driver_last_name", "driver last", "drv last", "driver_lname",
            "driver lastname", "drv_last", "driver_ln"
        ],
    },
    {
        "key": "dol",
        "label": "DOL",
        "required": False,
        "description": "Date of Loss (MM/DD/YYYY or Excel serial date)",
        "aliases": [
            "dol", "date of loss", "loss date", "date_of_loss",
            "accident date", "accident_date", "loss_date"
        ],
    },
    {
        "key": "policy_state",
        "label": "Policy State",
        "required": False,
        "description": "State where policy was issued (e.g. FL, TX)",
        "aliases": [
            "policy state", "policy_state", "pol state", "pol_state",
            "policy st", "pol_st", "state"
        ],
    },
    {
        "key": "loss_location_state",
        "label": "Loss Location State",
        "required": False,
        "description": "State where incident/loss occurred",
        "aliases": [
            "loss location state", "loss_location_state", "loss state",
            "loss_state", "accident state", "loss st"
        ],
    },
    {
        "key": "loss_location_city",
        "label": "Loss Location City",
        "required": False,
        "description": "City where incident/loss occurred",
        "aliases": [
            "loss location city", "loss_location_city", "loss city",
            "loss_city", "accident city"
        ],
    },
    {
        "key": "loss_location_county",
        "label": "Loss Location County",
        "required": False,
        "description": "County where incident/loss occurred",
        "aliases": [
            "loss location county", "loss_location_county", "loss county",
            "loss_county"
        ],
    },
    {
        "key": "garaging_city",
        "label": "Garaging City",
        "required": False,
        "description": "City where insured vehicle is garaged",
        "aliases": [
            "garaging city", "garaging_city", "garage city"
        ],
    },
    {
        "key": "garaging_state",
        "label": "Garaging State",
        "required": False,
        "description": "State where insured vehicle is garaged",
        "aliases": [
            "garaging state", "garaging_state", "garage state"
        ],
    },
    {
        "key": "exposure_number",
        "label": "Exposure Number",
        "required": False,
        "description": "Claim coverage exposure number (defaults to '001')",
        "aliases": [
            "exposure number", "exposure_number", "exposure #",
            "exposure", "exposure no", "exposure_no"
        ],
    },
    {
        "key": "primary_key",
        "label": "Primary Key",
        "required": False,
        "description": "External primary identifier",
        "aliases": [
            "primary key", "primary_key", "pk", "id", "record_id"
        ],
    },
]


def auto_detect_column_mapping(detected_columns: list[str]) -> list[dict[str, Any]]:
    """
    Intelligently map detected spreadsheet column headers to standard UAIC target fields.
    Uses exact alias matching and RapidFuzz scoring.
    """
    cleaned_detected = [str(c).strip() for c in detected_columns if str(c).strip()]
    normalized_detected = {c: c.lower().replace("_", " ").strip() for c in cleaned_detected}

    used_columns: set[str] = set()
    recommendations: list[dict[str, Any]] = []

    for field in TARGET_CLAIM_FIELDS:
        target_key = field["key"]
        target_label = field["label"]
        required = field["required"]
        aliases = [a.lower().strip() for a in field["aliases"]]

        best_match: str | None = None
        best_confidence = "UNMAPPED"
        best_score = 0.0

        # Pass 1: Exact alias match
        for orig_col, norm_col in normalized_detected.items():
            if orig_col in used_columns:
                continue
            if norm_col in aliases or orig_col.lower() in aliases:
                best_match = orig_col
                best_confidence = "EXACT"
                best_score = 1.0
                break

        # Pass 2: Fuzzy matching if no exact alias found
        if not best_match:
            highest_fuzzy = 0.0
            candidate_col: str | None = None
            for orig_col, norm_col in normalized_detected.items():
                if orig_col in used_columns:
                    continue
                # Calculate max similarity against target label and aliases
                scores = [
                    fuzz.token_sort_ratio(target_label.lower(), norm_col),
                    fuzz.ratio(target_label.lower(), norm_col),
                ]
                for alias in aliases[:4]:
                    scores.append(fuzz.token_sort_ratio(alias, norm_col))
                max_field_score = max(scores)
                if max_field_score > highest_fuzzy:
                    highest_fuzzy = max_field_score
                    candidate_col = orig_col

            if candidate_col and highest_fuzzy >= 75.0:
                best_match = candidate_col
                best_confidence = "HIGH_FUZZY"
                best_score = round(highest_fuzzy / 100.0, 2)
            elif candidate_col and highest_fuzzy >= 60.0:
                best_match = candidate_col
                best_confidence = "LOW_FUZZY"
                best_score = round(highest_fuzzy / 100.0, 2)

        if best_match:
            used_columns.add(best_match)

        recommendations.append({
            "target_key": target_key,
            "target_label": target_label,
            "source_column": best_match,
            "confidence": best_confidence,
            "confidence_score": best_score,
            "required": required,
        })

    return recommendations


def extract_columns_and_samples(df: pd.DataFrame, max_samples: int = 3) -> tuple[list[str], dict[str, list[str]]]:
    """Extract stripped column names and up to max_samples non-empty string samples per column."""
    columns = [str(col).strip() for col in df.columns]
    df.columns = columns
    samples: dict[str, list[str]] = {}

    for col in columns:
        col_samples: list[str] = []
        series = df[col].dropna()
        for val in series:
            s_val = str(val).strip()
            if s_val and s_val.lower() not in ["nan", "null", "none"]:
                col_samples.append(s_val)
                if len(col_samples) >= max_samples:
                    break
        samples[col] = col_samples

    return columns, samples


def validate_and_normalize_claim_data(
    df: pd.DataFrame,
    column_mapping: dict[str, str | None] | None = None,
    existing_claims: set[str] | None = None,
    duplicate_strategy: str = "SKIP",
) -> dict[str, Any]:
    """
    Validates, deduplicates, and normalizes dataframe rows according to the specified column mapping.
    Supports duplicate strategies: 'SKIP', 'OVERWRITE', 'IMPORT_ALL'.
    """
    df.columns = [str(col).strip() for col in df.columns]

    # Resolve mapping: map canonical target keys to source dataframe columns
    resolved_mapping: dict[str, str] = {}
    if column_mapping:
        for t_field in TARGET_CLAIM_FIELDS:
            key = t_field["key"]
            label = t_field["label"]
            # Check by key first, then by label
            src = column_mapping.get(key) or column_mapping.get(label)
            if src and src in df.columns:
                resolved_mapping[key] = src
    else:
        # Default legacy fallback or auto-detection
        recs = auto_detect_column_mapping(list(df.columns))
        for r in recs:
            if r.get("source_column") and r["source_column"] in df.columns:
                resolved_mapping[r["target_key"]] = r["source_column"]

    existing_set = existing_claims or set()

    total_rows = len(df)
    valid_rows = 0
    invalid_rows = 0
    duplicate_rows = 0
    florida_count = 0
    texas_count = 0
    cross_state_count = 0
    estimated_bots = 0

    seen_file_claims: set[str] = set()
    records_to_insert: list[dict[str, Any]] = []
    records_to_update: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    failed_rows_list: list[dict[str, Any]] = []
    preview_records: list[dict[str, Any]] = []

    for idx, row in df.iterrows():
        row_num = idx + 1
        raw_row_data = {str(k): (str(v) if not pd.isna(v) else "") for k, v in row.items()}

        def get_val(field_key: str) -> str | None:
            src_col = resolved_mapping.get(field_key)
            if not src_col or src_col not in row:
                return None
            val = row[src_col]
            if pd.isna(val) or val is None or str(val).strip().lower() in ["nan", "null", "none", ""]:
                return None
            return str(val).strip()

        # Check required Claim Number
        claim_num = get_val("claim_number")
        if not claim_num:
            invalid_rows += 1
            reason = f"Missing or empty required Claim Number (Mapped column: {resolved_mapping.get('claim_number', 'Not Mapped')})"
            issues.append({
                "row_number": row_num,
                "claim_number": None,
                "issue_type": "INVALID",
                "reason": reason,
            })
            failed_rows_list.append({
                "row_number": row_num,
                "claim_number": "-",
                "status": "INVALID",
                "reason": reason,
                **raw_row_data,
            })
            continue

        claim_num_str = str(claim_num).strip()

        # Duplicate check 1: In-file duplicate
        is_in_file_dup = claim_num_str in seen_file_claims
        seen_file_claims.add(claim_num_str)

        # Duplicate check 2: Database duplicate
        is_in_db_dup = claim_num_str in existing_set

        if is_in_file_dup or is_in_db_dup:
            duplicate_rows += 1
            dup_type = "DUPLICATE_IN_FILE" if is_in_file_dup else "DUPLICATE_IN_DB"
            dup_reason = (
                f"Duplicate claim number '{claim_num_str}' repeated within this spreadsheet"
                if is_in_file_dup
                else f"Claim number '{claim_num_str}' already exists in database"
            )
            issues.append({
                "row_number": row_num,
                "claim_number": claim_num_str,
                "issue_type": dup_type,
                "reason": dup_reason,
            })

            if duplicate_strategy == "SKIP":
                failed_rows_list.append({
                    "row_number": row_num,
                    "claim_number": claim_num_str,
                    "status": "DUPLICATE_SKIPPED",
                    "reason": dup_reason,
                    **raw_row_data,
                })
                continue

        # Valid row parsing
        valid_rows += 1

        ins_first = get_val("insured_first_name")
        ins_last = get_val("insured_last_name")
        ins_name = f"{ins_first or ''} {ins_last or ''}".strip() or None

        clm_first = get_val("claimant_first_name")
        clm_last = get_val("claimant_last_name")
        clm_name = f"{clm_first or ''} {clm_last or ''}".strip() or None

        drv_first = get_val("driver_first_name")
        drv_last = get_val("driver_last_name")
        drv_name = f"{drv_first or ''} {drv_last or ''}".strip() or None

        raw_dol = None
        if "dol" in resolved_mapping and resolved_mapping["dol"] in row:
            raw_dol = row[resolved_mapping["dol"]]
        dol_str = convert_excel_date(raw_dol)

        pol_state = get_val("policy_state") or "Florida"
        loss_state = get_val("loss_location_state") or pol_state
        loss_city = get_val("loss_location_city")
        loss_county = get_val("loss_location_county")
        garaging_city = get_val("garaging_city")
        garaging_state = get_val("garaging_state")
        exposure_num = get_val("exposure_number") or "001"
        primary_key = get_val("primary_key") or claim_num_str

        loss_loc_parts = [p for p in [loss_city, loss_county, loss_state] if p]
        loss_location_str = ", ".join(loss_loc_parts) or None

        targets = resolve_county_bot_targets(pol_state, loss_state)
        active_bots = [k.replace("fl_", "FL: ").replace("te_", "TX: ").title() for k, v in targets.items() if v == "Yes"]
        estimated_bots += len(active_bots)

        p_up = (pol_state or "").upper()
        l_up = (loss_state or "").upper()
        if p_up in ["FL", "FLORIDA"] and l_up in ["FL", "FLORIDA"]:
            florida_count += 1
        elif p_up in ["TX", "TEXAS"] and l_up in ["TX", "TEXAS"]:
            texas_count += 1
        else:
            cross_state_count += 1

        record_dict = {
            # Standard legacy keys
            "Claim Number": claim_num_str,
            "Insured First Name": ins_first,
            "Insured Last Name": ins_last,
            "Claimant First Name": clm_first,
            "Claimant Last Name": clm_last,
            "Driver First Name (Insured Vehicle)": drv_first,
            "Driver Last Name (Insured Vehicle)": drv_last,
            "DOL": dol_str,
            "Garaging City": garaging_city,
            "Garaging State": garaging_state,
            "Loss Location City": loss_city,
            "Loss Location County": loss_county,
            "Loss Location State": loss_state,
            "Policy State": pol_state,
            "Exposure Number": exposure_num,
            "Primary Key": primary_key,
            # Canonical snake_case keys
            "claim_number": claim_num_str,
            "insured_first_name": ins_first,
            "insured_last_name": ins_last,
            "claimant_first_name": clm_first,
            "claimant_last_name": clm_last,
            "driver_first_name": drv_first,
            "driver_last_name": drv_last,
            "dol": dol_str,
            "garaging_city": garaging_city,
            "garaging_state": garaging_state,
            "loss_location_city": loss_city,
            "loss_location_county": loss_county,
            "loss_location_state": loss_state,
            "policy_state": pol_state,
            "exposure_number": exposure_num,
            "primary_key": primary_key,
            "target_bots": targets,
            "active_bot_labels": active_bots,
        }

        if is_in_db_dup and duplicate_strategy == "OVERWRITE":
            records_to_update.append(record_dict)
        else:
            records_to_insert.append(record_dict)

        if len(preview_records) < 15:
            preview_records.append({
                "row_number": row_num,
                "claim_number": claim_num_str,
                "insured_name": ins_name,
                "claimant_name": clm_name,
                "driver_name": drv_name,
                "dol": dol_str,
                "policy_state": pol_state,
                "loss_location": loss_location_str,
                "target_bots": active_bots,
            })

    return {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "duplicate_rows": duplicate_rows,
        "records_to_insert": records_to_insert,
        "records_to_update": records_to_update,
        "issues": issues,
        "preview_records": preview_records,
        "failed_rows_list": failed_rows_list,
        "florida_count": florida_count,
        "texas_count": texas_count,
        "cross_state_count": cross_state_count,
        "estimated_bots": estimated_bots,
        "resolved_mapping": resolved_mapping,
    }


def parse_claim_file(
    file_path: str,
    column_mapping: dict[str, str | None] | None = None,
    existing_claims: set[str] | None = None,
    duplicate_strategy: str = "SKIP",
) -> list[dict[str, Any]]:
    """Reads Excel (.xlsx, .xls) or CSV file and normalizes columns into dictionaries."""
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, dtype=str)
    else:
        df = pd.read_excel(file_path)

    result = validate_and_normalize_claim_data(
        df=df,
        column_mapping=column_mapping,
        existing_claims=existing_claims,
        duplicate_strategy=duplicate_strategy,
    )

    # Return combined list for ingestion
    return result["records_to_insert"] + result["records_to_update"]

