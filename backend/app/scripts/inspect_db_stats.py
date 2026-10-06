import sqlite3

conn = sqlite3.connect('orchestrator.db')
c = conn.cursor()

print("=== CLAIM_RECORDS COUNT ===")
total_claims = c.execute("SELECT count(*) FROM claim_records").fetchone()[0]
print(f"Total claim_records: {total_claims}")

print("\n=== RECORD STATUSES ===")
statuses = c.execute("SELECT record_status, count(*) FROM claim_records GROUP BY record_status").fetchall()
for s, cnt in statuses:
    print(f"  {s}: {cnt}")

print("\n=== INGESTION BATCHES ===")
batches = c.execute("SELECT id, filename, total_records, processed_records, created_at FROM ingestion_batches").fetchall()
for b in batches:
    print(" ", b)

print("\n=== SAMPLE CLAIMS (First 10) ===")
rows = c.execute("SELECT id, claim_number, claimant_first_name, claimant_last_name, insured_first_name, insured_last_name, policy_state, record_status, created_at FROM claim_records ORDER BY created_at DESC LIMIT 10").fetchall()
for r in rows:
    print(" ", r)

print("\n=== SCRAPED COURT CASES COUNT BY PORTAL ===")
cases = c.execute("SELECT portal, count(*) FROM scraped_court_cases GROUP BY portal").fetchall()
print(f"Total portals with cases: {len(cases)}")
for p, cnt in cases:
    print(f"  {p}: {cnt}")

print("\n=== SCRAPED COURT CASES TOTAL COUNT ===")
total_cases = c.execute("SELECT count(*) FROM scraped_court_cases").fetchone()[0]
print(f"Total scraped_court_cases: {total_cases}")

print("\n=== CLAIMS WITH CASES IN scraped_court_cases ===")
claims_with_cases = c.execute("""
    SELECT c.id, c.claim_number, c.claimant_first_name, c.claimant_last_name, c.record_status, count(cc.id) as case_cnt
    FROM claim_records c
    LEFT JOIN scraped_court_cases cc ON cc.claim_id = c.id
    GROUP BY c.id
    HAVING count(cc.id) > 0
""").fetchall()
print(f"Number of claims with court_cases records: {len(claims_with_cases)}")
for row in claims_with_cases:
    print(" ", row)

conn.close()
