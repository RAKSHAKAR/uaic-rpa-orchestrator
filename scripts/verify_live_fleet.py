import httpx
import json
import time

def test_live_fleet():
    url = "http://localhost:8000/api/v1/settings/test-fleet"
    payload = {
        "concurrency": 10,
        "browser_engine": "chromium",
        "headless": True,
        "timeout_seconds": 120,
    }
    print(f"Calling {url} with concurrency=10 (headless=True, timeout_seconds=120)...")
    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=220.0) as client:
            resp = client.post(url, json=payload)
            elapsed = time.perf_counter() - t0
            print(f"Status Code: {resp.status_code} in {elapsed:.2f}s")
            data = resp.json()
            print("Response Summary:")
            print(f"  Success: {data.get('success')}")
            print(f"  Requested: {data.get('concurrency_requested')}")
            print(f"  Succeeded: {data.get('concurrency_succeeded')}")
            print(f"  Browser Engine: {data.get('browser_engine')}")
            print(f"  Total Duration: {data.get('total_fleet_duration_ms', 0):.0f} ms")
            print(f"  Workers Count: {len(data.get('workers', []))}")
            for w in data.get("workers", []):
                print(f"    Worker #{w.get('worker_id')}: status={w.get('status')} duration={w.get('duration_ms', 0):.0f}ms ext={w.get('extension_loaded')}")
            return data.get("success") is True and data.get("concurrency_succeeded") == 10
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_live_fleet()
    exit(0 if success else 1)
