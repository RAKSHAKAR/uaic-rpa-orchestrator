"""
deep_reconciliation.py - Detailed requirement extraction and codebase inspection.
"""

import os
import sys
import glob
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Inspect actual backend routes
backend_api_dir = os.path.join(REPO_ROOT, "backend", "app", "api", "v1", "endpoints")
endpoints = {}
for f in os.listdir(backend_api_dir):
    if f.endswith(".py") and not f.startswith("__"):
        fpath = os.path.join(backend_api_dir, f)
        with open(fpath, "r", encoding="utf-8") as fp:
            content = fp.read()
        routes = re.findall(r'@router\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', content)
        endpoints[f] = routes

print("=== ACTUAL BACKEND ENDPOINTS ===")
total_endpoints = 0
for mod, rts in endpoints.items():
    print(f"[{mod}] ({len(rts)} endpoints):")
    for method, path in rts:
        print(f"  {method.upper():6} {path}")
        total_endpoints += 1
print(f"Total API endpoints in backend: {total_endpoints}\n")

# Inspect actual models
models_dir = os.path.join(REPO_ROOT, "backend", "app", "models")
models = {}
for f in os.listdir(models_dir):
    if f.endswith(".py") and not f.startswith("__"):
        fpath = os.path.join(models_dir, f)
        with open(fpath, "r", encoding="utf-8") as fp:
            content = fp.read()
        classes = re.findall(r'class\s+([A-Za-z0-9_]+)\(Base\):', content)
        cols = re.findall(r'([a-zA-Z0-9_]+)\s*=\s*Column\(', content)
        models[f] = {"classes": classes, "columns": cols}

print("=== ACTUAL BACKEND MODELS ===")
for mod, info in models.items():
    print(f"[{mod}]: Classes: {info['classes']}, Columns ({len(info['columns'])}): {info['columns']}")
print()

# Inspect actual frontend pages and routes
frontend_app_dir = os.path.join(REPO_ROOT, "frontend", "src", "app")
fe_routes = []
for root, dirs, files in os.walk(frontend_app_dir):
    for file in files:
        if file in ("page.tsx", "page.js"):
            rel = os.path.relpath(root, frontend_app_dir)
            route = "/" if rel == "." else "/" + rel.replace("\\", "/")
            fe_routes.append(route)

print(f"=== ACTUAL FRONTEND ROUTES ({len(fe_routes)}) ===")
for r in sorted(fe_routes):
    print(f"  {r}")
print()

# Inspect scrapers
scrapers_fl = os.listdir(os.path.join(REPO_ROOT, "backend", "app", "automation", "florida"))
scrapers_tx = os.listdir(os.path.join(REPO_ROOT, "backend", "app", "automation", "texas"))
print("=== ACTUAL AUTOMATION SCRAPERS ===")
print("Florida:", [s for s in scrapers_fl if not s.startswith("__")])
print("Texas:  ", [s for s in scrapers_tx if not s.startswith("__")])
print()

# Inspect tests count
tests_dir = os.path.join(REPO_ROOT, "backend", "tests")
test_files = [f for f in os.listdir(tests_dir) if f.startswith("test_") and f.endswith(".py")]
print(f"=== BACKEND TESTS ({len(test_files)} test files) ===")
for tf in sorted(test_files):
    with open(os.path.join(tests_dir, tf), "r", encoding="utf-8") as fp:
        c = fp.read()
    test_funcs = re.findall(r'def (test_[a-zA-Z0-9_]+)', c)
    print(f"  {tf}: {len(test_funcs)} tests")
