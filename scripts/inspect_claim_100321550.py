import sqlite3

conn = sqlite3.connect("backend/orchestrator.db")
c = conn.cursor()
c.execute("""
    SELECT claim_number, policy_state, loss_location_state, 
           te_website_travis, te_botstatus_travis, 
           te_website_dallas, te_botstatus_dallas, 
           te_website_harris, te_botstatus_harris, 
           te_website_cclerk, te_botstatus_cclerk, 
           te_website_hcdistrict, te_botstatus_hcdistrict,
           action_timings
    FROM claim_records 
    WHERE claim_number='100321550'
""")
row = c.fetchone()
col_names = [d[0] for d in c.description]
for name, val in zip(col_names, row):
    if name == "action_timings":
        print(f"{name}: {str(val)[:300]}")
    else:
        print(f"{name}: {val}")
conn.close()
