import httpx
import json

TARGET_CLAIMS = [
    "100285627",
    "100319958",
    "100305433",
    "100295866",
    "800221263",
    "100294077",
]

def check_claims():
    client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30.0)
    
    # Check queue status first
    q_res = client.get("/queue/status")
    print(f"Queue Status: {q_res.json()}")
    
    # Check each target claim
    for cnum in TARGET_CLAIMS:
        res = client.get(f"/claims?search={cnum}&limit=5")
        if res.status_code == 200:
            items = res.json().get("items", [])
            matches = [c for c in items if c.get("claim_number") == cnum]
            if matches:
                c = matches[0]
                print(f"Claim #{cnum} (ID: {c.get('id')}) | State: {c.get('policy_state')} | Status: {c.get('record_status')} | Error: {c.get('error_message')}")
                print(f"   FL Bots: Broward={c.get('fl_broward_status')}, Hills={c.get('fl_hillsborough_status')}, Miami={c.get('fl_miami_status')}")
                print(f"   TX Bots: HarrisJP={c.get('te_harris_status')}, CClerk={c.get('te_cclerk_status')}, HCDist={c.get('te_hcdistrict_status')}, Dallas={c.get('te_dallas_status')}, Travis={c.get('te_travis_status')}")
            else:
                print(f"Claim #{cnum}: Not found in search")
        else:
            print(f"Claim #{cnum}: HTTP {res.status_code}")

if __name__ == "__main__":
    check_claims()
