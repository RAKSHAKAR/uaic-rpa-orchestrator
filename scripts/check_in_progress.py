import sqlite3
import json

conn = sqlite3.connect("orchestrator.db")
c = conn.cursor()
c.execute("SELECT id, claim_number, updated_at, created_at, action_timings FROM claim_records WHERE record_status = 'SCRAPING_IN_PROGRESS'")
rows = c.fetchall()
print(f"Found {len(rows)} claims in SCRAPING_IN_PROGRESS:")
for r in rows:
    timings = json.loads(r[4]) if r[4] else {}
    print(f"ID: {r[0]} | Claim#: {r[1]} | Updated: {r[2]} | Timings started_at: {timings.get('started_at')}")
conn.close()
