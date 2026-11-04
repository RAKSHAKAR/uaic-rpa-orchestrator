import urllib.request
import json

endpoints = [
    ("FastAPI Health", "http://127.0.0.1:8000/api/v1/health"),
    ("FastAPI Claims Stats", "http://127.0.0.1:8000/api/v1/claims/stats"),
    ("FastAPI Queue Status", "http://127.0.0.1:8000/api/v1/queue/status"),
    ("Frontend Home", "http://127.0.0.1:3000/"),
    ("MailDev API", "http://127.0.0.1:1080/email"),
    ("Celery Flower", "http://127.0.0.1:5555/"),
]

for name, url in endpoints:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = resp.getcode()
            print(f"[{code}] {name}: OK ({url})")
    except Exception as e:
        print(f"[ERR] {name}: {e} ({url})")

