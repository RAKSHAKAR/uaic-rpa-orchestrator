import urllib.request
import json

url = "http://localhost:8000/api/v1/claims/81231115-de71-4ea4-a018-ba5b794df682"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode())

print("=== RECORD STATUS ===")
print("record_status:", data.get("record_status"))
print("last_error:", data.get("last_error"))
print("total_duration_seconds:", data.get("total_duration_seconds"))

print("\n=== BOTS ===")
for b in data.get("bots", []):
    print(f"- {b.get('name')}: target={b.get('target')}, status={b.get('status')}, cases={b.get('cases_found')}, err={b.get('error_message')}")

print("\n=== ACTION TIMINGS ===")
print(json.dumps(data.get("action_timings"), indent=2))
