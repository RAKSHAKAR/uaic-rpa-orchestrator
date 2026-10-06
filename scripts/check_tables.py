import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "backend" / "orchestrator.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print("Tables in orchestrator.db:", tables)

for t in ["automation_settings", "settings_audit_logs"]:
    if t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        print(f"\nColumns in {t}:", [c[1] for c in cur.fetchall()])
    else:
        print(f"\nMISSING TABLE: {t}")

conn.close()
