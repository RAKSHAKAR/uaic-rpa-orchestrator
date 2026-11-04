import subprocess

import redis


def remediate():
    print("=== Step 1: Cleaning Redis Leaked Locks ===")
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=0, socket_connect_timeout=2.0)
        r.ping()
        print("Connected to Redis successfully.")
        
        # Keys to delete
        deleted_count = 0
        for k in ["uaic:browser:active_count", "uaic:browser:active_claims", "uaic:queue:active_item_ids", "uaic:queue:active_item_id"]:
            if r.exists(k):
                r.delete(k)
                print(f"Deleted Redis key: {k}")
                deleted_count += 1
                
        # Also clean any stale cooldowns so bots can run cleanly
        cooldown_keys = r.keys("uaic:cooldown:*")
        for ck in cooldown_keys:
            r.delete(ck)
            print(f"Cleared cooldown key: {ck.decode('utf-8')}")
            deleted_count += 1
            
        print(f"Redis cleanup complete: {deleted_count} keys cleared.")
    except Exception as e:
        print(f"Redis cleanup note: {e}")

    print("\n=== Step 2: Remediating Failed Claims in Docker PostgreSQL (uaic_db) ===")
    psql_cmd = [
        "docker", "exec", "uaic_postgres", "psql", "-U", "postgres", "-d", "uaic_db", "-c",
        """
        UPDATE claim_records
        SET record_status = 'NEW',
            retry_count = 0,
            last_error = NULL,
            fl_botstatus_broward = CASE WHEN fl_botstatus_broward IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE fl_botstatus_broward END,
            fl_botstatus_hillsborough = CASE WHEN fl_botstatus_hillsborough IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE fl_botstatus_hillsborough END,
            fl_botstatus_miami = CASE WHEN fl_botstatus_miami IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE fl_botstatus_miami END,
            te_botstatus_travis = CASE WHEN te_botstatus_travis IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE te_botstatus_travis END,
            te_botstatus_dallas = CASE WHEN te_botstatus_dallas IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE te_botstatus_dallas END,
            te_botstatus_harris = CASE WHEN te_botstatus_harris IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE te_botstatus_harris END,
            te_botstatus_cclerk = CASE WHEN te_botstatus_cclerk IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE te_botstatus_cclerk END,
            te_botstatus_hcdistrict = CASE WHEN te_botstatus_hcdistrict IN ('IN_PROGRESS', 'FAILED', 'BLOCKED') THEN 'NOT_TRIGGERED' ELSE te_botstatus_hcdistrict END
        WHERE record_status = 'FAILED' OR record_status = 'SCRAPING_IN_PROGRESS';
        """
    ]
    try:
        res = subprocess.run(psql_cmd, capture_output=True, text=True, check=True)
        print("PostgreSQL update result:", res.stdout.strip())
    except Exception as e:
        print("PostgreSQL update note:", e)

    print("\n=== Step 3: Checking Claim Statuses in PostgreSQL ===")
    check_cmd = [
        "docker", "exec", "uaic_postgres", "psql", "-U", "postgres", "-d", "uaic_db", "-c",
        "SELECT record_status, count(*) FROM claim_records GROUP BY record_status;"
    ]
    try:
        res = subprocess.run(check_cmd, capture_output=True, text=True, check=True)
        print(res.stdout.strip())
    except Exception as e:
        print("PostgreSQL check note:", e)

if __name__ == "__main__":
    remediate()
