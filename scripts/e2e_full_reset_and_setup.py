"""
Full reset for proper live E2E test:
1. Kill active Redis queue locks
2. Delete all claims
3. Disable auto-queue so we control exactly when claims run
4. Upload both Excel files fresh
5. Verify settings are correct
"""
import json
import urllib.request
import urllib.error
import subprocess
import sys

BASE = "http://localhost:8000/api/v1"

def api(method, path, body=None, quiet=False):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.load(r)
            if not quiet:
                print(f"  {method} {path} -> OK")
            return result
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"  {method} {path} -> ERROR {e.code}: {body_text[:200]}")
        return {"error": e.code}

print("=" * 65)
print("STEP 1: PAUSE AUTO-QUEUE")
print("=" * 65)
r = api("POST", "/queue/pause")
print(f"  Result: {r}")

# Also disable auto-mode via the toggle
r2 = api("POST", "/queue/auto-mode", {"enabled": False})
print(f"  Auto-mode disabled: {r2}")

print()
print("=" * 65)
print("STEP 2: DELETE ALL CLAIMS")
print("=" * 65)
claims_resp = api("GET", "/claims?page=1&page_size=100", quiet=True)
all_ids = [c["id"] for c in claims_resp.get("items", [])]
print(f"  Found {len(all_ids)} claims to delete")
if all_ids:
    del_result = api("POST", "/claims/bulk-delete", {"claim_ids": all_ids})
    print(f"  Deleted: {del_result.get('affected_count', 0)} claims")

stats = api("GET", "/claims/stats", quiet=True)
print(f"  DB after cleanup: {stats}")

print()
print("=" * 65)
print("STEP 3: VERIFY SETTINGS")
print("=" * 65)
s = api("GET", "/settings", quiet=True)
auto = s.get("automation", {})
key = auto.get("anticaptcha_api_key", "")
masked = ("***" + key[-6:]) if key and len(key) > 6 else "(NOT SET - PROBLEM!)"
print(f"  AntiCaptcha Key    : {masked}")
print(f"  Extension Verified : {auto.get('extension_setup_verified', False)}")
print(f"  Max Concurrent     : {auto.get('max_concurrent_claims', 1)}")
print(f"  Headless           : {auto.get('headless_mode', False)}")
print(f"  AntiCaptcha On     : {auto.get('anticaptcha_enabled', False)}")
print(f"  Chrome Path        : {auto.get('chrome_binary_path', 'NOT SET')}")
print(f"  Extension Dir      : {auto.get('chrome_extension_dir', 'NOT SET')}")

queue_cfg = s.get("queue", {})
print(f"  Auto Retry Failed  : {queue_cfg.get('auto_retry_failed_scrapes', True)}")

print()
print("=" * 65)
print("STEP 4: UPLOAD EXCEL FILES")
print("=" * 65)
# Florida
fl_result = subprocess.run(
    ["curl.exe", "-s", "-X", "POST", f"{BASE}/ingest/upload",
     "-F", "file=@Testing files\\sample_claims - Florida.xlsx"],
    cwd=r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC",
    capture_output=True, text=True
)
fl_resp = json.loads(fl_result.stdout)
print(f"  FL Upload: {fl_resp.get('filename')} -> status={fl_resp.get('status')}, id={fl_resp.get('id')}")

# Texas
tx_result = subprocess.run(
    ["curl.exe", "-s", "-X", "POST", f"{BASE}/ingest/upload",
     "-F", "file=@Testing files\\5RecordsTexas.xlsx"],
    cwd=r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC",
    capture_output=True, text=True
)
tx_resp = json.loads(tx_result.stdout)
print(f"  TX Upload: {tx_resp.get('filename')} -> status={tx_resp.get('status')}, id={tx_resp.get('id')}")

import time
print("  Waiting 8s for ingest workers...")
time.sleep(8)

print()
print("=" * 65)
print("STEP 5: CLAIMS INGESTED - READY FOR CONTROLLED START")
print("=" * 65)
claims_resp = api("GET", "/claims?page=1&page_size=20&sort_by=created_at&sort_dir=asc", quiet=True)
total = claims_resp.get("total", 0)
print(f"  Total claims ready: {total}")
print()
print(f"  {'#':<3} {'Claim Number':<15} {'State':<10} {'Loss State':<10} {'Status'}")
print(f"  {'-'*3} {'-'*15} {'-'*10} {'-'*10} {'-'*15}")
for i, c in enumerate(claims_resp.get("items", []), 1):
    print(f"  {i:<3} {c.get('claim_number',''):<15} {c.get('policy_state',''):<10} {c.get('loss_location_state',''):<10} {c.get('record_status', c.get('status',''))}")

print()
print("=" * 65)
print("READY FOR MANUAL CONTROLLED START")
print("Auto-queue is DISABLED. Claims will ONLY run when you")
print("click Start or when this script starts them deliberately.")
print("=" * 65)
print()
print("CLAIM IDs FOR MANUAL START:")
for c in claims_resp.get("items", []):
    print(f"  {c.get('claim_number',''):<15} -> {c.get('id')}")
