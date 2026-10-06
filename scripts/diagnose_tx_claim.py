import urllib.request
import json

url = "http://localhost:8000/api/v1/claims/57d46e31-e1f9-41c8-b8bb-6071ce6697d1"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print("Status Code:", resp.status)
        print("Claim Number:", data.get("claim_number"))
        print("Overall Status:", data.get("status"))
        print("Total Duration:", data.get("total_duration_seconds"))
        print("Action Timings:", json.dumps(data.get("action_timings"), indent=2))
        print("Error Screenshots:", len(data.get("error_screenshots", [])))
        for es in data.get("error_screenshots", []):
            print("  Screenshot:", es.get("portal_name"), es.get("error_message"), es.get("file_path"))
        print("Stage Statuses:", json.dumps(data.get("stage_statuses"), indent=2))
        print("Cases Count:", len(data.get("court_cases", [])))
except Exception as e:
    print("Error:", e)
