#!/usr/bin/env python
"""
UAIC Orchestrator Setup & Maintenance Tool.
Provides installation, system diagnostics, and optional clean-history commands.

Usage:
    python setup.py                     # Check environment & setup
    python setup.py --clean-history     # Clean all Celery worker queues & DB records
    python setup.py --clean-all         # Clean history, caches, and temp files
    python setup.py --check             # Run system diagnostics
    python setup.py --test              # Run 46-test verification suite
"""

import sys
import os
import argparse
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def get_python_executable():
    """Detect python executable inside backend .venv or fallback."""
    venv_py = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        return venv_py
    venv_py2 = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_py2):
        return venv_py2
    return sys.executable


def clean_history():
    """Purge all Celery queues, Redis broker keys, and DB claim records."""
    print("\n[+] Purging worker queues and database records...")
    py_exe = get_python_executable()
    clean_script = os.path.join(BACKEND_DIR, "app", "scripts", "clean_history.py")
    res = subprocess.run([py_exe, clean_script], cwd=BACKEND_DIR)
    if res.returncode == 0:
        print("\n[SUCCESS] Successfully cleaned all worker queues and database history.")
    else:
        print("\n[ERROR] Failed to clean worker history.")
        sys.exit(res.returncode)


def clean_all():
    """Purge history, clean .next cache, and remove temp profiles."""
    clean_history()
    print("\n[+] Cleaning frontend .next cache...")
    next_dir = os.path.join(FRONTEND_DIR, ".next")
    if os.path.exists(next_dir):
        try:
            shutil.rmtree(next_dir, ignore_errors=True)
        except Exception as e:
            print(f"  - Could not remove .next: {e}")
            
    print("\n[+] Cleaning Python __pycache__ directories...")
    for root, dirs, files in os.walk(BACKEND_DIR):
        for d in dirs:
            if d == "__pycache__":
                pycache_path = os.path.join(root, d)
                try:
                    shutil.rmtree(pycache_path, ignore_errors=True)
                except Exception:
                    pass
    print("  - Removed stale Python bytecode caches")

    print("\n[SUCCESS] Full cleanup complete.")


def run_checks():
    """Check Redis, Python, and frontend dependencies."""
    print("==================================================")
    print("   UAIC Orchestrator - Environment Diagnostics    ")
    print("==================================================")
    py_exe = get_python_executable()
    print(f"Python Executable: {py_exe}")

    # Check Redis
    print("\n1. Checking Redis Connection...")
    try:
        check_cmd = [
            py_exe,
            "-c",
            "import redis; r = redis.Redis.from_url('redis://localhost:6379/0'); r.ping(); print('OK')",
        ]
        res = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and "OK" in res.stdout:
            print("   [OK] Redis is running on localhost:6379")
        else:
            err = res.stderr.strip() or res.stdout.strip()
            print(f"   [WARN] Redis check failed: {err}")
    except Exception as e:
        print(f"   [WARN] Redis check failed: {e}")

    # Check Database
    print("\n2. Checking SQLite Database...")
    db_path = os.path.join(BACKEND_DIR, "orchestrator.db")
    if os.path.exists(db_path):
        size_kb = os.path.getsize(db_path) / 1024
        print(f"   [OK] orchestrator.db exists ({size_kb:.1f} KB)")
    else:
        print("   [INFO] orchestrator.db does not exist yet (will be created automatically)")

    # Check Node modules
    print("\n3. Checking Frontend Dependencies...")
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if os.path.exists(node_modules):
        print("   [OK] frontend/node_modules exists")
    else:
        print("   [WARN] frontend/node_modules is missing. Run 'npm install' in frontend/")


def run_tests():
    """Run full pytest suite."""
    print("\n[+] Running backend verification test suite...")
    py_exe = get_python_executable()
    pytest_exe = os.path.join(os.path.dirname(py_exe), "pytest.exe")
    cmd = [pytest_exe] if os.path.exists(pytest_exe) else [py_exe, "-m", "pytest"]
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND_DIR
    res = subprocess.run(cmd, cwd=BACKEND_DIR, env=env)
    sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="UAIC Orchestrator Setup & Maintenance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--clean-history",
        action="store_true",
        help="Purge all Celery worker queues, Redis tasks, and database claim history",
    )
    parser.add_argument(
        "--clean-all",
        action="store_true",
        help="Purge queues, database history, and reset frontend cache",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run environment health diagnostics",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run backend pytest test suite",
    )

    args = parser.parse_args()

    if args.clean_history:
        clean_history()
    elif args.clean_all:
        clean_all()
    elif args.check:
        run_checks()
    elif args.test:
        run_tests()
    else:
        run_checks()
        print("\nTip: Run 'python setup.py --clean-history' anytime to clear worker queues and claim history.")


if __name__ == "__main__":
    main()
