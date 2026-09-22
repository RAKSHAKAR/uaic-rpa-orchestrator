"""Read and display current system settings cleanly."""
import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

with urllib.request.urlopen(f"{BASE}/settings", timeout=10) as r:
    s = json.load(r)

print("=" * 60)
print("CURRENT SYSTEM SETTINGS")
print("=" * 60)

# AntiCaptcha
key = s.get("anti_captcha_api_key") or ""
masked = ("***" + key[-6:]) if key and len(key) > 6 else "(NOT SET)"
print(f"\n[ANTICAPTCHA]")
print(f"  API Key         : {masked}")

# Browser / Fleet
br = s.get("browser") or {}
print(f"\n[BROWSER / FLEET]")
print(f"  Mode            : {br.get('mode', s.get('browser_mode', 'NOT SET'))}")
print(f"  Fleet Size      : {br.get('fleet_size', br.get('concurrency', s.get('fleet_size', 'NOT SET')))}")
print(f"  Headless        : {br.get('headless', s.get('headless', 'NOT SET'))}")
print(f"  Chrome Path     : {br.get('chrome_path', s.get('chrome_path', 'NOT SET'))}")
ext = br.get("anticaptcha_extension_enabled", s.get("anticaptcha_extension_enabled", "NOT SET"))
print(f"  Extension       : {ext}")

# Proxy
px = s.get("proxy") or {}
print(f"\n[PROXY]")
print(f"  Enabled         : {px.get('enabled', False)}")
print(f"  Host:Port       : {px.get('host','(none)')}:{px.get('port','')}")

# Guidewire
gw = s.get("guidewire") or {}
mock = gw.get("mock_mode", s.get("mock_mode", s.get("guidewire_mock_mode", "NOT SET")))
url = gw.get("api_url", s.get("guidewire_api_url", "NOT SET"))
print(f"\n[GUIDEWIRE]")
print(f"  Mock Mode       : {mock}")
print(f"  API URL         : {str(url)[:70]}")

# Fuzzy match threshold
thresh = s.get("fuzzy_threshold", s.get("match_threshold", "NOT SET"))
min_date = s.get("min_filing_date", "NOT SET")
print(f"\n[MATCHING]")
print(f"  Fuzzy Threshold : {thresh}")
print(f"  Min Filing Date : {min_date}")

# Top-level keys - show everything raw for debugging
print(f"\n[ALL TOP-LEVEL KEYS]")
for k in sorted(s.keys()):
    v = s[k]
    if isinstance(v, dict):
        print(f"  {k}: {{...}}")
    elif isinstance(v, str) and len(v) > 80:
        print(f"  {k}: {v[:77]}...")
    else:
        print(f"  {k}: {v}")
