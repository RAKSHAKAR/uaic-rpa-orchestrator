"""
UAIC Claim & RPA Orchestrator - Multi-Engine Fleet Concurrency Test Suite
Tests Concurrency 1 to 10 across:
1. Google Chrome ('chrome')
2. Chromium ('chromium')
3. Microsoft Edge ('msedge')
"""

import json
import sys
import urllib.request
import urllib.error
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/settings/test-fleet"

def test_fleet(engine: str, concurrency: int, headless: bool = True):
    print(f"\n========================================================")
    print(f"Testing Fleet: Engine={engine.upper()} | Concurrency={concurrency} | Headless={headless}")
    print(f"========================================================")

    payload = {
        "concurrency": concurrency,
        "browser_engine": engine,
        "headless": headless,
        "test_url": "http://127.0.0.1:8000/api/v1/settings/browser-test-page",
        "timeout_seconds": 120,
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            status_code = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            dur = round((time.perf_counter() - t0), 2)
            print(f"HTTP Status: {status_code} ({dur}s)")
            print(f"Fleet Success: {body.get('success')}")
            print(f"Requested: {body.get('concurrency_requested')} | Succeeded: {body.get('concurrency_succeeded')}")
            print(f"Total Fleet Latency: {body.get('total_fleet_duration_ms')}ms")
            print(f"Message: {body.get('message')}")
            workers = body.get("workers", [])
            for w in workers:
                print(f"  - Worker #{w.get('worker_id')}: status={w.get('status')}, duration={w.get('duration_ms')}ms, title='{w.get('window_title')}', ext={w.get('extension_loaded')}")
            
            if body.get("success") and body.get("concurrency_succeeded") == concurrency:
                print(f"--> PASS: {engine.upper()} with {concurrency} workers verified successfully!")
                return True
            else:
                print(f"--> FAIL: Incomplete concurrency {body.get('concurrency_succeeded')}/{concurrency}")
                return False
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP Error {e.code}: {err_body}")
        return False
    except Exception as e:
        print(f"Exception during fleet test: {e}")
        return False


if __name__ == "__main__":
    target_engine = sys.argv[1] if len(sys.argv) > 1 else "chrome"
    target_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    is_headless = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True

    success = test_fleet(target_engine, target_concurrency, is_headless)
    sys.exit(0 if success else 1)
