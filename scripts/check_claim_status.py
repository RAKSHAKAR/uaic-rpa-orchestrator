"""Quick claim status checker for E2E verification."""
import json
import sys
import urllib.request

BASE = "http://localhost:8000/api/v1"

CLAIMS = {
    "FL-100285580": "7cef8e45-b2c0-445d-9bd3-20c7f853c132",
    "TX-100292772": "37b1c28b-25d7-404e-9222-cdb985997e08",
}

print("=" * 70)
print("E2E CLAIM STATUS CHECK")
print("=" * 70)

for label, cid in CLAIMS.items():
    url = f"{BASE}/claims/{cid}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.load(r)
        print(f"\n[{label}]")
        print(f"  Status        : {d.get('status', 'N/A')}")
        print(f"  Claim Number  : {d.get('claim_number', 'N/A')}")
        print(f"  Policy State  : {d.get('policy_state', 'N/A')}")
        print(f"  Loss State    : {d.get('loss_location_state', 'N/A')}")
        pr = d.get("portal_results") or {}
        if pr:
            print(f"  Portal Keys   : {list(pr.keys())}")
            for k, v in pr.items():
                if isinstance(v, list):
                    print(f"    {k}: {len(v)} records")
                elif isinstance(v, dict):
                    print(f"    {k}: {v.get('status', str(v))}")
        else:
            print("  Portal Results: (none yet)")
        print(f"  Updated At    : {d.get('updated_at', 'N/A')}")
    except Exception as e:
        print(f"\n[{label}] ERROR: {e}")

# Print queue stats
print("\n" + "=" * 70)
print("QUEUE STATUS")
print("=" * 70)
try:
    with urllib.request.urlopen(f"{BASE}/queue/status", timeout=10) as r:
        q = json.load(r)
    print(json.dumps(q, indent=2))
except Exception as e:
    print(f"Queue error: {e}")

# Print stats
print("\n" + "=" * 70)
print("CLAIMS AGGREGATE STATS")
print("=" * 70)
try:
    with urllib.request.urlopen(f"{BASE}/claims/stats", timeout=10) as r:
        s = json.load(r)
    print(json.dumps(s, indent=2))
except Exception as e:
    print(f"Stats error: {e}")
