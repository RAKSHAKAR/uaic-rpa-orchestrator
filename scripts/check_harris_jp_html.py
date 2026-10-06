import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print("Status:", resp.status)
        print("HTML length:", len(html))
        print("Contains recaptcha:", "recaptcha" in html.lower())
        print("Contains hcaptcha:", "hcaptcha" in html.lower())
        print("Contains turnstile:", "turnstile" in html.lower())
        print("Contains smart search:", "smart search" in html.lower())
        print("Contains caseCriteria:", "caseCriteria" in html)
        print("Title:", html[html.find("<title>"):html.find("</title>")+8] if "<title>" in html else "No title")
except Exception as e:
    print("Error:", e)
