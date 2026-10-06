import sqlite3

conn = sqlite3.connect("orchestrator.db")
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", tables)

for t in tables:
    name = t[0]
    if "claim" in name.lower():
        c.execute(f"SELECT record_status, count(*) FROM {name} GROUP BY record_status")
        print(f"Status count for {name}:", c.fetchall())
conn.close()
