"""Sanitizer script to purge all occurrences of @test.com across code, databases, Redis, and configuration.
Replaces @test.com with @test.com.
"""
import os
import sqlite3
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IGNORE_DIRS = {".git", ".venv", "node_modules", ".next", ".pytest_cache", ".ruff_cache", "__pycache__"}

print("=" * 70)
print("PURGING ALL OCCURRENCES OF @test.com -> @test.com")
print("=" * 70)

# 1. Check all text files
text_files_updated = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
    for fname in filenames:
        if fname.endswith((".py", ".ts", ".tsx", ".js", ".json", ".md", ".env", ".example", ".txt", ".sql", ".bat", ".ps1")):
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Check case insensitive @test.com
                if "@test.com" in content.lower():
                    # Replace while matching case or standard replacement
                    new_content = content
                    for old_variant in ["@test.com", "@test.com", "@test.com", "@test.com"]:
                        new_content = new_content.replace(old_variant, "@test.com")
                    
                    if new_content != content:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        rel = os.path.relpath(fpath, ROOT)
                        print(f"Updated text file: {rel}")
                        text_files_updated += 1
            except Exception as e:
                print(f"Error processing {fpath}: {e}")

print(f"Total text files updated: {text_files_updated}")

# 2. Check SQLite databases
for db_rel in ["backend/orchestrator.db", "backend/orchestrator.db.bak"]:
    db_path = os.path.join(ROOT, db_rel)
    if os.path.exists(db_path):
        print(f"\nProcessing SQLite database: {db_rel}")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        db_updates = 0
        for t in tables:
            cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t});").fetchall()]
            for col in cols:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {t} WHERE {col} LIKE '%@test.com%' OR {col} LIKE '%@test.com%';")
                    cnt = cur.fetchone()[0]
                    if cnt > 0:
                        cur.execute(f"UPDATE {t} SET {col} = REPLACE({col}, '@test.com', '@test.com') WHERE {col} LIKE '%@test.com%';")
                        cur.execute(f"UPDATE {t} SET {col} = REPLACE({col}, '@test.com', '@test.com') WHERE {col} LIKE '%@test.com%';")
                        db_updates += cnt
                        print(f"  Replaced {cnt} rows in {t}.{col}")
                except Exception as e:
                    # Non-text or read error
                    pass
        conn.commit()
        conn.close()
        print(f"Total SQLite rows updated in {db_rel}: {db_updates}")

# 3. Check Redis cache if Redis is available
try:
    import redis
    r = redis.Redis.from_url("redis://localhost:6379/0", socket_timeout=1)
    keys = r.keys("uaic:*")
    redis_updates = 0
    for k in keys:
        val = r.get(k)
        if val and b"@test.com" in val.lower():
            val_str = val.decode("utf-8", errors="ignore")
            new_val_str = val_str.replace("@test.com", "@test.com").replace("@test.com", "@test.com")
            r.set(k, new_val_str)
            print(f"Updated Redis key: {k.decode('utf-8', errors='ignore')}")
            redis_updates += 1
    print(f"Total Redis keys updated: {redis_updates}")
except Exception as e:
    print(f"Redis check skipped / not running: {e}")

print("\nSanitization complete!")
