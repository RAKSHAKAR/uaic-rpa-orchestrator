import sqlite3
import json

DB_PATH = r"backend/orchestrator.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== SEARCHING AUDIT LOGS FOR BROWARD AND MIAMI EXCEPTIONS ===")
    cursor.execute("""
        SELECT action, claim_number, description, details, timestamp
        FROM audit_logs
        WHERE (description LIKE '%Broward%' OR description LIKE '%Miami%')
          AND (status = 'FAILURE' OR description LIKE '%fail%' OR description LIKE '%error%')
        ORDER BY timestamp DESC LIMIT 15
    """)
    for r in cursor.fetchall():
        print(f"\n[{r['timestamp']}] Claim: {r['claim_number']} | Action: {r['action']}")
        print(f"  Desc: {r['description']}")
        print(f"  Details: {r['details']}")

    print("\n=== SEARCHING ERROR SCREENSHOTS DETAILS ===")
    cursor.execute("""
        SELECT portal_key, portal_name, page_url, exception_message, attempt_number, file_path, created_at
        FROM error_screenshots
        WHERE portal_key IN ('broward', 'miami')
          AND exception_message NOT LIKE 'Discovery:%'
        ORDER BY created_at DESC LIMIT 10
    """)
    for r in cursor.fetchall():
        print(f"\n[{r['created_at']}] Portal: {r['portal_key']} | Attempt: {r['attempt_number']}")
        print(f"  URL: {r['page_url']}")
        print(f"  Msg: {r['exception_message']}")
        print(f"  File: {r['file_path']}")

    conn.close()

if __name__ == '__main__':
    main()
