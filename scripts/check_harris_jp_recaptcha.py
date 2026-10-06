import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'<[^>]*recaptcha[^>]*>', html, flags=re.IGNORECASE)
        print("Recaptcha tags found:", len(matches))
        for m in matches:
            print("  ", m)
        scripts = re.findall(r'<script[^>]*src=[^>]*>', html, flags=re.IGNORECASE)
        for s in scripts:
            if "recaptcha" in s.lower() or "google" in s.lower() or "captcha" in s.lower():
                print("  Script:", s)
except Exception as e:
    print("Error:", e)
