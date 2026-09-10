import urllib.request
import sys

claim_id = sys.argv[1] if len(sys.argv) > 1 else '32b240c2-8a7a-43a7-aa50-5f7358645f1c'
print(f"Testing exports for claim_id: {claim_id}")

for fmt in ['json', 'csv', 'xlsx', 'pdf']:
    url = f"http://127.0.0.1:8000/api/v1/claims/{claim_id}/export?format={fmt}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type")
            cd = resp.headers.get("Content-Disposition")
            print(f"{fmt.upper()}: Status {resp.status}, Content-Type: {ct}, Disposition: {cd}, Size: {len(data)} bytes")
            print(f"   First 60 bytes: {data[:60]}")
            # Save to disk to inspect
            filename = f"scratch_test_{claim_id[:8]}.{fmt}"
            with open(filename, "wb") as f:
                f.write(data)
            print(f"   Saved to {filename}")
    except Exception as e:
        print(f"{fmt.upper()} ERROR: {type(e).__name__}: {e}")
        if hasattr(e, 'read'):
            try:
                err_body = e.read().decode('utf-8', errors='ignore')
                print(f"   Error body: {err_body}")
            except Exception:
                pass
