import sqlite3
import json

DB_PATH = r"backend/orchestrator.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("==================================================")
    print("=== CLAIM RECORD STATUS COUNTS ===")
    print("==================================================")
    cursor.execute("SELECT record_status, count(*) FROM claim_records GROUP BY record_status")
    for row in cursor.fetchall():
        print(f"Status: {row[0]:<25} | Count: {row[1]}")

    cursor.execute("SELECT count(*) FROM claim_records")
    total = cursor.fetchone()[0]
    print(f"Total claims in database: {total}")

    print("\n==================================================")
    print("=== FAILED CLAIMS ANALYSIS ===")
    print("==================================================")
    cursor.execute("""
        SELECT id, claim_number, policy_state, loss_location_state, record_status,
               total_duration_seconds, last_error, action_timings,
               fl_botstatus_broward, fl_botstatus_hillsborough, fl_botstatus_miami,
               te_botstatus_cclerk, te_botstatus_dallas, te_botstatus_harris, te_botstatus_hcdistrict, te_botstatus_travis,
               created_at, updated_at
        FROM claim_records
        WHERE record_status = 'FAILED' OR last_error IS NOT NULL
        ORDER BY updated_at DESC
    """)
    failed_rows = cursor.fetchall()
    print(f"Total failed/error records found: {len(failed_rows)}")
    for r in failed_rows:
        dur_min = (r['total_duration_seconds'] or 0) / 60
        print(f"\n[CLAIM #{r['claim_number']}] (ID: {r['id'][:8]})")
        print(f"  Routing: Policy={r['policy_state']}, Loss={r['loss_location_state']} | Status: {r['record_status']}")
        print(f"  Duration: {dur_min:.2f} min ({r['total_duration_seconds']}s) | Updated: {r['updated_at']}")
        print(f"  Last Error: {r['last_error']}")
        
        # Check portal statuses
        p_statuses = {}
        for col in ['fl_botstatus_broward', 'fl_botstatus_hillsborough', 'fl_botstatus_miami',
                    'te_botstatus_cclerk', 'te_botstatus_dallas', 'te_botstatus_harris', 'te_botstatus_hcdistrict', 'te_botstatus_travis']:
            val = r[col]
            if val and val != 'NOT_TRIGGERED':
                p_statuses[col] = val
        print(f"  Portals Triggered: {p_statuses}")

        # Check action timings for details
        if r['action_timings']:
            timings = r['action_timings']
            if isinstance(timings, str):
                try:
                    timings = json.loads(timings)
                except Exception:
                    timings = {}
            if isinstance(timings, dict):
                portals = timings.get('portals', {})
                for p_name, p_data in portals.items():
                    print(f"    Portal [{p_name}]: status={p_data.get('status')}, duration={p_data.get('duration_seconds')}s, error={p_data.get('error')}")
                    stages = p_data.get('stages', {})
                    for s_name, s_data in stages.items():
                        print(f"      - {s_name}: {s_data.get('duration_seconds')}s, status={s_data.get('status')}")

    print("\n==================================================")
    print("=== SLOW CLAIMS ANALYSIS (> 300 SECONDS / > 5 MIN) ===")
    print("==================================================")
    cursor.execute("""
        SELECT id, claim_number, policy_state, loss_location_state, record_status,
               total_duration_seconds, last_error, action_timings, updated_at
        FROM claim_records
        WHERE total_duration_seconds > 300
        ORDER BY total_duration_seconds DESC
    """)
    slow_rows = cursor.fetchall()
    print(f"Total claims taking > 5 min: {len(slow_rows)}")
    for r in slow_rows:
        dur_min = (r['total_duration_seconds'] or 0) / 60
        print(f"\n[CLAIM #{r['claim_number']}] (ID: {r['id'][:8]})")
        print(f"  Routing: Policy={r['policy_state']}, Loss={r['loss_location_state']} | Status: {r['record_status']}")
        print(f"  Total Duration: {dur_min:.2f} min ({r['total_duration_seconds']}s)")
        print(f"  Last Error: {r['last_error']}")
        if r['action_timings']:
            timings = r['action_timings']
            if isinstance(timings, str):
                try:
                    timings = json.loads(timings)
                except Exception:
                    timings = {}
            if isinstance(timings, dict):
                portals = timings.get('portals', {})
                for p_name, p_data in portals.items():
                    print(f"    Portal [{p_name}]: status={p_data.get('status')}, duration={p_data.get('duration_seconds')}s, error={p_data.get('error')}")
                    stages = p_data.get('stages', {})
                    for s_name, s_data in stages.items():
                        print(f"      - {s_name}: {s_data.get('duration_seconds')}s, status={s_data.get('status')}")

    print("\n==================================================")
    print("=== ERROR SCREENSHOTS ===")
    print("==================================================")
    cursor.execute("""
        SELECT portal, claim_id, error_message, file_path, created_at
        FROM error_screenshots
        ORDER BY created_at DESC LIMIT 15
    """)
    for r in cursor.fetchall():
        print(f"[{r['created_at']}] Portal: {r['portal']:<15} | Claim: {r['claim_id'][:8]} | File: {r['file_path']} | Err: {r['error_message']}")

    print("\n==================================================")
    print("=== RECENT AUDIT LOG ERRORS / FAILURES ===")
    print("==================================================")
    cursor.execute("""
        SELECT action, entity_id, claim_number, description, status, timestamp, details
        FROM audit_logs
        WHERE status IN ('FAILURE', 'ERROR') OR action LIKE '%FAIL%' OR description LIKE '%fail%' OR description LIKE '%error%'
        ORDER BY timestamp DESC LIMIT 20
    """)
    for r in cursor.fetchall():
        print(f"[{r['timestamp']}] Action: {r['action']} | Claim: {r['claim_number']} | Desc: {r['description']} | Details: {str(r['details'])[:150]}")

    conn.close()

if __name__ == '__main__':
    main()
