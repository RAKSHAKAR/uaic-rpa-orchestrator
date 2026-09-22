"""Deep-inspect all nested settings to find AntiCaptcha key, fleet, browser mode."""
import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

with urllib.request.urlopen(f"{BASE}/settings", timeout=10) as r:
    s = json.load(r)

print("=" * 70)
print("FULL SETTINGS DEEP DUMP")
print("=" * 70)

def show(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                show(v, full_key)
            else:
                # Mask API keys
                val = str(v)
                if any(x in k.lower() for x in ["key", "password", "secret", "token"]) and len(val) > 8:
                    val = val[:4] + "***" + val[-4:]
                print(f"  {full_key}: {val}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            show(item, f"{prefix}[{i}]")

show(s)
