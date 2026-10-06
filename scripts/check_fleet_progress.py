import httpx

def check_progress():
    client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30.0)
    
    stats_res = client.get("/claims/stats")
    print(f"Claims Stats: {stats_res.json()}")
    
    # Check status of some newly completed claims or active claims
    recent = client.get("/claims?limit=10&sort_by=updated_at&sort_desc=true")
    if recent.status_code == 200:
        items = recent.json().get("items", [])
        print("\n10 Most Recently Updated Claims:")
        for c in items:
            print(f"- Claim #{c.get('claim_number')} (ID: {c.get('id')[:8]}) | Status: {c.get('record_status')} | FL: ({c.get('fl_broward_status')}, {c.get('fl_hillsborough_status')}, {c.get('fl_miami_status')}) | TX: ({c.get('te_harris_status')}, {c.get('te_cclerk_status')}, {c.get('te_hcdistrict_status')})")

if __name__ == "__main__":
    check_progress()
