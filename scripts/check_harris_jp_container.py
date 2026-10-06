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
        pos = html.find("data-sitekey")
        if pos != -1:
            snippet = html[max(0, pos-500):min(len(html), pos+500)]
            print("Snippet around recaptcha:\n", snippet)
        else:
            print("data-sitekey not found")
except Exception as e:
    print("Error:", e)
