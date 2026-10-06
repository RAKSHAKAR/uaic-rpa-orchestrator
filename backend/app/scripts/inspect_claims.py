import json

import httpx

claim_ids = [
    "03d75d35-bde6-451f-b81e-158cabf6a524",
    "5bedd37c-e94c-4c8a-9f61-3bf72e06d896",
    "3292f711-ab3a-4e30-82dd-60051bcca720",
]

with httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30.0) as client:
    for cid in claim_ids:
        r = client.get(f"/claims/{cid}")
        if r.status_code != 200:
            print(f"Claim {cid} HTTP {r.status_code}: {r.text}")
            continue
        data = r.json()
        print(f"=== CLAIM #{data.get('claim_number')} ({cid}) ===")
        print(f"Status: {data.get('record_status')}")
        print(f"Policy State: {data.get('policy_state')}, Loss State: {data.get('loss_location_state')}")
        print(f"Insured: {data.get('insured_name')}, Claimant: {data.get('claimant_name')}, Driver: {data.get('driver_name')}")
        print(f"Exception Details: {data.get('exception_details')}")
        print(f"Portal Results: {json.dumps(data.get('portal_results'), indent=2)}")
        print(f"Court cases count: {len(data.get('scraped_cases', []))}")
        
        # Check combined logs
        r_logs = client.get(f"/claims/{cid}/logs")
        if r_logs.status_code == 200:
            logs_data = r_logs.json()
            audit_logs = logs_data.get("audit_logs", [])
            print(f"Audit logs count: {len(audit_logs)}")
            for al in audit_logs[:5]:
                print(f"  [Audit] {al.get('timestamp')}: {al.get('action')} - {str(al.get('detail'))[:120]}")
            
            exc_logs = logs_data.get("exception_logs", [])
            print(f"Exception logs count: {len(exc_logs)}")
            for el in exc_logs[:5]:
                print(f"  [Exception] {el.get('timestamp')}: {el.get('source')} - {el.get('message')} - {str(el.get('traceback'))[:120]}")
        print("\n" + "=" * 50 + "\n")
