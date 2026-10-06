import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.celery_app import celery_app

print("Pinging workers with timeout=2.0s...")
res = celery_app.control.ping(timeout=2.0)
print("Ping result:", res)
