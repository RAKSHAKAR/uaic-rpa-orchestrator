import urllib.request
import json
import sys

claim_id = sys.argv[1] if len(sys.argv) > 1 else "81231115-de71-4ea4-a018-ba5b794df682"
url = f"http://localhost:8000/api/v1/claims/{claim_id}"
req = urllib.request.urlopen(url)
d = json.load(req)

print("=" * 60)
print(f"CLAIM ID: {claim_id}")
print(f"Claim Number : {d.get('claim_number')}")
print(f"Record Status: {d.get('record_status')}")
print(f"Fuzzy Status : {d.get('fuzzy_match_status')}")
print(f"Stages       : {d.get('stages_completed')}/{d.get('stages_total')}")
print(f"Duration     : {d.get('total_duration_seconds')}s")
print(f"Last Error   : {d.get('last_error')}")
print("Bots:")
for b in d.get("bots", []):
    if b.get("target") == "Yes":
        print(f"  - {b['name']}: {b['status']} ({b['cases_found']} cases)")
print("=" * 60)
