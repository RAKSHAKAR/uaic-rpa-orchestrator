import sqlite3
import os

root_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "orchestrator.db"))
backend_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "orchestrator.db"))

print(f"Root DB: {root_db} (exists: {os.path.exists(root_db)})")
print(f"Backend DB: {backend_db} (exists: {os.path.exists(backend_db)})")

conn_src = sqlite3.connect(root_db)
conn_dst = sqlite3.connect(backend_db)

cur_src = conn_src.cursor()
cur_src.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur_src.fetchall() if not t[0].startswith('sqlite_')]
print("Tables in root DB:", tables)

for tbl in tables:
    cur_src.execute(f"SELECT count(*) FROM {tbl}")
    cnt_src = cur_src.fetchone()[0]
    try:
        cur_dst = conn_dst.cursor()
        cur_dst.execute(f"SELECT count(*) FROM {tbl}")
        cnt_dst = cur_dst.fetchone()[0]
        print(f"  {tbl}: src={cnt_src}, dst={cnt_dst}")
    except Exception as e:
        print(f"  {tbl}: src={cnt_src}, dst error={e}")

conn_src.close()
conn_dst.close()
