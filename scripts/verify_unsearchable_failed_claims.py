import sqlite3
import sys
sys.path.insert(0, 'backend')
from app.services.fuzzy_engine import is_unsearchable_party, generate_unique_names_for_claim

conn = sqlite3.connect('backend/orchestrator.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, claim_number, insured_first_name, insured_last_name, driver_first_name, driver_last_name, claimant_first_name, claimant_last_name, last_error FROM claim_records WHERE record_status = 'FAILED'")
rows = cursor.fetchall()
print(f"Total FAILED claims: {len(rows)}")

unsearchable_count = 0
all_unsearchable_count = 0

for r in rows:
    ins_un = is_unsearchable_party(r['insured_first_name'], r['insured_last_name'])
    drv_un = is_unsearchable_party(r['driver_first_name'], r['driver_last_name'])
    clm_un = is_unsearchable_party(r['claimant_first_name'], r['claimant_last_name'])
    
    unique_targets = generate_unique_names_for_claim(dict(r))
    
    if ins_un or drv_un or clm_un:
        unsearchable_count += 1
        print(f"Claim #{r['claim_number']}: Insured={r['insured_first_name']} {r['insured_last_name']} (unsearchable={ins_un}), Driver={r['driver_first_name']} {r['driver_last_name']} (unsearchable={drv_un}), Claimant={r['claimant_first_name']} {r['claimant_last_name']} (unsearchable={clm_un}) -> Filtered Targets: {len(unique_targets)}")
    if len(unique_targets) == 0:
        all_unsearchable_count += 1

print(f"\nSummary:")
print(f"  Claims with at least one unsearchable party: {unsearchable_count}")
print(f"  Claims where ALL parties are unsearchable (bypassed instantly): {all_unsearchable_count}")

conn.close()
