import sqlite3
import json
from collections import defaultdict, Counter

DB_PATH = r"backend/orchestrator.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Total counts by status
    cursor.execute("SELECT record_status, count(*) FROM claim_records GROUP BY record_status")
    status_counts = dict(cursor.fetchall())

    # 2. Duration statistics
    cursor.execute("SELECT count(*) FROM claim_records WHERE total_duration_seconds > 600")
    over_10_min = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM claim_records WHERE total_duration_seconds > 300 AND total_duration_seconds <= 600")
    between_5_and_10_min = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM claim_records WHERE total_duration_seconds > 0 AND total_duration_seconds <= 300")
    under_5_min = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM claim_records WHERE total_duration_seconds IS NULL OR total_duration_seconds = 0")
    no_duration = cursor.fetchone()[0]

    # Average durations by routing
    cursor.execute("""
        SELECT 
            CASE 
                WHEN policy_state = 'Florida' OR policy_state = 'FL' THEN 'FL'
                WHEN policy_state = 'Texas' OR policy_state = 'TX' THEN 'TX'
                ELSE 'CROSS_STATE'
            END as state_group,
            count(*),
            avg(total_duration_seconds),
            max(total_duration_seconds),
            min(total_duration_seconds)
        FROM claim_records
        WHERE total_duration_seconds > 0
        GROUP BY state_group
    """)
    duration_by_group = [dict(r) for r in cursor.fetchall()]

    # 3. Analyze failure reasons
    cursor.execute("""
        SELECT id, claim_number, policy_state, loss_location_state, record_status,
               last_error, retry_count, total_duration_seconds, action_timings,
               fl_botstatus_broward, fl_botstatus_hillsborough, fl_botstatus_miami,
               te_botstatus_cclerk, te_botstatus_dallas, te_botstatus_harris, te_botstatus_hcdistrict, te_botstatus_travis
        FROM claim_records
        WHERE record_status = 'FAILED' OR last_error IS NOT NULL
    """)
    failed_claims = cursor.fetchall()
    
    failure_reasons = Counter()
    portal_failures = Counter()
    detailed_failed_list = []

    for r in failed_claims:
        err = r['last_error'] or "Unknown error"
        # Categorize error
        if "Scraping timed out or was interrupted" in err:
            cat = "Timeout / Interrupted by worker restart"
        elif "Broward County" in err:
            cat = "Broward County scraper failure"
        elif "Miami-Dade" in err:
            cat = "Miami-Dade scraper failure"
        elif "Hillsborough" in err:
            cat = "Hillsborough scraper failure"
        elif "Travis" in err:
            cat = "Travis scraper failure"
        elif "Dallas" in err:
            cat = "Dallas scraper failure"
        elif "Harris" in err:
            cat = "Harris scraper failure"
        elif "database is locked" in err.lower():
            cat = "Database locked"
        elif "connection" in err.lower() or "timeout" in err.lower():
            cat = "Network / Connection timeout"
        else:
            cat = f"Other: {err[:60]}"
        failure_reasons[cat] += 1

        for col in ['fl_botstatus_broward', 'fl_botstatus_hillsborough', 'fl_botstatus_miami',
                    'te_botstatus_cclerk', 'te_botstatus_dallas', 'te_botstatus_harris', 'te_botstatus_hcdistrict', 'te_botstatus_travis']:
            if r[col] == 'FAILED':
                portal_failures[col.replace('fl_botstatus_', 'FL_').replace('te_botstatus_', 'TX_')] += 1

        detailed_failed_list.append({
            "claim_number": r["claim_number"],
            "states": f"{r['policy_state']}/{r['loss_location_state']}",
            "status": r["record_status"],
            "duration_s": r["total_duration_seconds"],
            "error": r["last_error"],
            "category": cat
        })

    # 4. Analyze slow claims (> 600s / 10min and > 300s / 5min)
    cursor.execute("""
        SELECT id, claim_number, policy_state, loss_location_state, total_duration_seconds, action_timings
        FROM claim_records
        WHERE total_duration_seconds > 300
        ORDER BY total_duration_seconds DESC
    """)
    slow_claims = cursor.fetchall()

    portal_avg_durations = defaultdict(list)
    stage_avg_durations = defaultdict(list)

    for r in slow_claims:
        timings = r['action_timings']
        if isinstance(timings, str):
            try:
                timings = json.loads(timings)
            except Exception:
                timings = None
        if isinstance(timings, dict):
            portals = timings.get('portals', {})
            for p_name, p_data in portals.items():
                dur = p_data.get('duration_seconds')
                if dur is not None:
                    portal_avg_durations[p_name].append(dur)
                stages = p_data.get('stages', {})
                for s_name, s_data in stages.items():
                    sdur = s_data.get('duration_seconds')
                    if sdur is not None:
                        stage_avg_durations[f"{p_name}:{s_name}"].append(sdur)

    portal_summary = {}
    for p, durs in portal_avg_durations.items():
        portal_summary[p] = {
            "count": len(durs),
            "avg_seconds": round(sum(durs) / len(durs), 2),
            "max_seconds": round(max(durs), 2),
            "min_seconds": round(min(durs), 2),
        }

    stage_summary = {}
    for s, durs in stage_avg_durations.items():
        stage_summary[s] = {
            "count": len(durs),
            "avg_seconds": round(sum(durs) / len(durs), 2),
            "max_seconds": round(max(durs), 2)
        }

    # 5. Error screenshots
    cursor.execute("""
        SELECT portal_key, portal_name, page_url, exception_message, count(*) as cnt
        FROM error_screenshots
        GROUP BY portal_key, exception_message
        ORDER BY cnt DESC
    """)
    screenshot_errors = [dict(r) for r in cursor.fetchall()]

    result = {
        "status_counts": status_counts,
        "duration_distribution": {
            "over_10_min": over_10_min,
            "between_5_and_10_min": between_5_and_10_min,
            "under_5_min": under_5_min,
            "no_duration": no_duration
        },
        "duration_by_group": duration_by_group,
        "failure_reasons_counter": dict(failure_reasons),
        "portal_failures_counter": dict(portal_failures),
        "portal_duration_summary": portal_summary,
        "stage_duration_summary": stage_summary,
        "screenshot_errors": screenshot_errors,
        "sample_failed_claims": detailed_failed_list[:15]
    }

    with open("scripts/analysis_output.json", "w") as f:
        json.dump(result, f, indent=2)

    print("SUCCESS: analysis_output.json created.")
    print(json.dumps({
        "status_counts": status_counts,
        "duration_distribution": result["duration_distribution"],
        "failure_reasons": dict(failure_reasons),
        "portal_failures": dict(portal_failures),
        "portal_duration_summary": portal_summary
    }, indent=2))

    conn.close()

if __name__ == '__main__':
    main()
