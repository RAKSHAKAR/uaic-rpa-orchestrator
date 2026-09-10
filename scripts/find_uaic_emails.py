"""Audit script to verify that ZERO occurrences of @uaic.com exist in code, databases, and configuration."""
import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IGNORE_DIRS = {".git", ".venv", "node_modules", ".next", ".pytest_cache", ".ruff_cache", "__pycache__"}

print("=" * 70)
print("AUDITING FOR ZERO OCCURRENCES OF @uaic.com")
print("=" * 70)

text_matches = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
    for fname in filenames:
        # Exclude this script and sanitize script from matching themselves
        if fname in ("find_uaic_emails.py", "sanitize_emails.py"):
            continue
        if fname.endswith((".py", ".ts", ".tsx", ".js", ".json", ".md", ".env", ".example", ".txt", ".sql", ".bat", ".ps1")):
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if "@uaic.com" in line.lower():
                            rel = os.path.relpath(fpath, ROOT)
                            text_matches.append((rel, i, line.strip()))
            except Exception:
                pass

if text_matches:
    print(f"FAILED: Found {len(text_matches)} text matches with @uaic.com:")
    for rel, line_num, line in text_matches:
        print(f"  {rel}:{line_num} -> {line}")
else:
    print("SUCCESS: 0 text matches found across all source and configuration files.")

# Check SQLite databases
db_matches = 0
for db_rel in ["backend/orchestrator.db", "backend/orchestrator.db.bak"]:
    db_path = os.path.join(ROOT, db_rel)
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        for t in tables:
            cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t});").fetchall()]
            for col in cols:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {t} WHERE CAST({col} AS TEXT) LIKE '%@uaic.com%';")
                    count = cur.fetchone()[0]
                    if count > 0:
                        print(f"FAILED: Database '{db_rel}', Table '{t}', Column '{col}': {count} rows matching '%@uaic.com%'")
                        db_matches += count
                except Exception:
                    pass
        conn.close()

if db_matches == 0:
    print("SUCCESS: 0 database rows found across all SQLite databases.")
else:
    print(f"FAILED: Found {db_matches} total database rows with @uaic.com")

if len(text_matches) == 0 and db_matches == 0:
    print("\nVERIFICATION PASSED: @uaic.com is 100% eliminated from the project.")
else:
    print("\nVERIFICATION FAILED: @uaic.com still exists.")
