import urllib.request
import re

html = urllib.request.urlopen("http://localhost:3000/", timeout=15).read().decode("utf-8")
m = re.search(r'href="(/_next/static/css/[^"]+)"', html)
if m:
    css_url = "http://localhost:3000" + m.group(1)
    print("Found CSS URL:", css_url)
    css_data = urllib.request.urlopen(css_url, timeout=15).read()
    print("CSS Data Length:", len(css_data))
    print("First 200 chars:", css_data[:200].decode("utf-8", errors="ignore"))
else:
    print("NO CSS link found in HTML!")
