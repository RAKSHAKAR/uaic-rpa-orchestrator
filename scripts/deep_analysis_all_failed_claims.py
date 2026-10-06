import sqlite3
import json
import os
from collections import defaultdict, Counter

DB_PATH = r"backend/orchestrator.db"
LOGS_DIR = r"backend/logs"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query all failed claim records
    cursor.execute("""
        SELECT id, claim_number, policy_state, loss_location_state, record_status,
               insured_first_name, insured_last_name, claimant_first_name, claimant_last_name, driver_first_name, driver_last_name,
               dol, retry_count, total_duration_seconds, last_error, action_timings,
               fl_website_broward, fl_botstatus_broward, fl_jsonbody_broward,
               fl_website_hillsborough, fl_botstatus_hillsborough, fl_jsonbody_hillsborough,
               fl_website_miami, fl_botstatus_miami, fl_jsonbody_miami,
               te_website_travis, te_botstatus_travis, te_jsonbody_travis,
               te_website_dallas, te_botstatus_dallas, te_jsonbody_dallas,
               te_website_harris, te_botstatus_harris, te_jsonbody_harris,
               te_website_cclerk, te_botstatus_cclerk, te_jsonbody_cclerk,
               te_website_hcdistrict, te_botstatus_hcdistrict, te_jsonbody_hcdistrict,
               created_at, updated_at
        FROM claim_records
        WHERE record_status = 'FAILED'
        ORDER BY updated_at DESC
    """)
    failed_claims = cursor.fetchall()
    print(f"Total failed claims found in DB: {len(failed_claims)}")

    error_categories = Counter()
    portal_failures = Counter()
    party_name_issues = []
    claims_details = []

    for c in failed_claims:
        cid = c['id']
        cnum = c['claim_number']
        err = c['last_error'] or "None"
        
        # Categorize
        if "Scraping timed out or was interrupted" in err or "Interrupted by worker restart" in err:
            cat = "Worker Timeout / Restart Interruption (10 min threshold)"
        elif "No searchable party surname" in err:
            cat = "Missing / Unsearchable Party Name"
        elif "Broward County" in err:
            cat = "Broward Scraper Failure"
        elif "Miami-Dade" in err:
            cat = "Miami-Dade Scraper Failure"
        elif "Hillsborough" in err:
            cat = "Hillsborough Scraper Failure"
        elif "Harris" in err:
            cat = "Harris Scraper Failure"
        elif "All required portals are in cooldown" in err:
            cat = "Portals in Security Cooldown"
        elif "Fleet concurrency limit reached" in err:
            cat = "Concurrency Slot Timeout"
        else:
            cat = f"Other: {err[:60]}"
        error_categories[cat] += 1

        # Check party names for patterns like "Unknown", "Dept", "LLC", etc.
        parties = [
            ("Insured", c['insured_first_name'], c['insured_last_name']),
            ("Claimant", c['claimant_first_name'], c['claimant_last_name']),
            ("Driver", c['driver_first_name'], c['driver_last_name']),
        ]
        for role, fn, ln in parties:
            full = f"{fn or ''} {ln or ''}".strip().upper()
            if any(term in full for term in ["UNKNOWN", "DEPARTMENT", "DEPT", "GOVERNMENT", "CITY OF", "STATE OF", "INC", "LLC", "CORP", "CO."]):
                party_name_issues.append({"claim_number": cnum, "role": role, "name": full})

        # Inspect execution logs from backend/logs/{cid}
        log_dir = os.path.join(LOGS_DIR, cid)
        portal_logs = {}
        if os.path.exists(log_dir):
            for portal_folder in os.listdir(log_dir):
                exec_file = os.path.join(log_dir, portal_folder, "execution.log")
                if os.path.exists(exec_file):
                    try:
                        with open(exec_file, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            # grab last 5 lines
                            portal_logs[portal_folder] = [line.strip() for line in lines[-5:]]
                    except Exception:
                        pass

        # Check portal statuses
        bot_statuses = {}
        for bcol in ['fl_botstatus_broward', 'fl_botstatus_hillsborough', 'fl_botstatus_miami',
                     'te_botstatus_travis', 'te_botstatus_dallas', 'te_botstatus_harris',
                     'te_botstatus_cclerk', 'te_botstatus_hcdistrict']:
            val = c[bcol]
            if val and val != 'NOT_TRIGGERED':
                bot_statuses[bcol] = val
                if val == 'FAILED':
                    portal_failures[bcol] += 1

        claims_details.append({
            "id": cid,
            "claim_number": cnum,
            "policy_state": c['policy_state'],
            "loss_state": c['loss_location_state'],
            "error_category": cat,
            "last_error": err,
            "duration_s": c['total_duration_seconds'],
            "bot_statuses": bot_statuses,
            "portal_logs": portal_logs,
            "parties": [(p[0], f"{p[1] or ''} {p[2] or ''}".strip()) for p in parties]
        })

    # Summary
    report = {
        "total_failed_claims": len(failed_claims),
        "error_categories": dict(error_categories),
        "portal_failures": dict(portal_failures),
        "party_name_issues_count": len(party_name_issues),
        "sample_party_name_issues": party_name_issues[:20],
        "detailed_claims": claims_details
    }

    with open("scripts/failed_claims_detailed_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("=== ERROR CATEGORIES SUMMARY ===")
    for k, v in error_categories.most_common():
        print(f"  {k:<55}: {v}")

    print("\n=== PORTAL FAILURES BREAKDOWN ===")
    for k, v in portal_failures.most_common():
        print(f"  {k:<30}: {v}")

    print(f"\nParty name issues found: {len(party_name_issues)}")
    for p in party_name_issues[:10]:
        print(f"  Claim {p['claim_number']} ({p['role']}): {p['name']}")

    conn.close()

if __name__ == '__main__':
    main()
