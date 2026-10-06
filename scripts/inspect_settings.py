import sqlite3
import json

conn = sqlite3.connect("backend/orchestrator.db")
c = conn.cursor()
c.execute("SELECT settings_json FROM system_settings WHERE id='global_settings'")
row = c.fetchone()
if row:
    data = json.loads(row[0])
    print("=== PORTAL SETTINGS ===")
    print(json.dumps(data.get("portals", {}), indent=2))
    print("=== AUTOMATION SETTINGS ===")
    print(json.dumps(data.get("automation", {}), indent=2))
    print("=== QUEUE SETTINGS ===")
    print(json.dumps(data.get("queue", {}), indent=2))
else:
    print("No global_settings found!")
conn.close()
