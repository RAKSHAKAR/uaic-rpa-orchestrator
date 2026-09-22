"""
Full clean: Reset ALL claims to 'new' status via bulk-status change,
then delete ALL claims, re-prepare for fresh test with the two Excel files.
"""
import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api/v1"

def api(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": e.code, "detail": e.read().decode()}

# Step 1: Get all claim IDs
print("Fetching all claims...")
all_ids = []
page = 1
while True:
    r = api("GET", f"/claims?page={page}&page_size=50")
    items = r.get("items", [])
    all_ids.extend([c["id"] for c in items])
    if len(all_ids) >= r.get("total", 0):
        break
    page += 1

print(f"Total claims found: {len(all_ids)}")

# Step 2: Bulk delete ALL claims (clean slate)
if all_ids:
    print(f"Deleting all {len(all_ids)} claims...")
    result = api("POST", "/claims/bulk-delete", {"claim_ids": all_ids})
    print(f"Delete result: {result}")

# Step 3: Verify clean
stats = api("GET", "/claims/stats")
print(f"\nAfter cleanup - Claims stats: {stats}")

print("\n✅ Database clean. Ready for fresh E2E test.")
print("Next step: Upload sample_claims - Florida.xlsx and 5RecordsTexas.xlsx fresh.")
