import base64
import json
import os
import subprocess
import sys
import time

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
VENV_PYTHON = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")


def make_encoded_cmd(title: str, script: str) -> str:
    full_script = f"$host.UI.RawUI.WindowTitle = '{title}'\n{script}"
    return base64.b64encode(full_script.encode("utf-16le")).decode("ascii")


def launch_window(title: str, script: str):
    encoded = make_encoded_cmd(title, script)
    subprocess.Popen(
        [
            "powershell.exe",
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-EncodedCommand",
            encoded,
        ],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def restart_celery_fleet():
    print("1. Querying existing Celery processes...")
    try:
        out = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Select-Object ProcessId, CommandLine | ConvertTo-Json -Depth 2",
            ],
            text=True,
        )
        procs = json.loads(out)
        if isinstance(procs, dict):
            procs = [procs]
    except Exception as e:
        print(f"Error querying processes: {e}")
        procs = []

    stale_pids = []
    for p in procs:
        cmd = (p.get("CommandLine") or "").lower()
        pid = p.get("ProcessId")
        if "celery" in cmd:
            stale_pids.append(pid)

    print(f"2. Terminating {len(stale_pids)} stale Celery process(es): {stale_pids}")
    for pid in stale_pids:
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                timeout=5,
            )
            print(f"   Terminated PID {pid}")
        except Exception as e:
            print(f"   Could not terminate PID {pid}: {e}")

    time.sleep(2)
    print("3. Stale Celery processes cleaned up.")

    print("4. Launching fresh Celery worker, beat, and flower...")
    worker_script = (
        f"Set-Location '{BACKEND_DIR}'; & '{VENV_PYTHON}' -m celery -A app.core.celery_app.celery_app "
        f"worker -E --loglevel=info -Q ingest,scrapers,matcher,notifications,default --pool=threads --concurrency=10"
    )
    launch_window("Celery Worker [Attended RPA]", worker_script)
    print("   Launched Celery Worker in interactive window.")

    beat_script = (
        f"Set-Location '{BACKEND_DIR}'; & '{VENV_PYTHON}' -m celery -A app.core.celery_app.celery_app beat --loglevel=info"
    )
    launch_window("Celery Beat Scheduler", beat_script)
    print("   Launched Celery Beat Scheduler in interactive window.")

    flower_script = (
        f"Set-Location '{BACKEND_DIR}'; & '{VENV_PYTHON}' -m celery -A app.core.celery_app.celery_app flower --port=5555"
    )
    launch_window("Celery Flower Monitor (port 5555)", flower_script)
    print("   Launched Celery Flower Monitor in interactive window.")

    time.sleep(4)
    print("5. Verifying newly launched Celery processes...")
    try:
        out = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Select-Object ProcessId, CommandLine | ConvertTo-Json -Depth 2",
            ],
            text=True,
        )
        new_procs = json.loads(out)
        if isinstance(new_procs, dict):
            new_procs = [new_procs]
        new_celery = [p for p in new_procs if "celery" in (p.get("CommandLine") or "").lower()]
        print(f"   Active fresh Celery process count: {len(new_celery)}")
        for p in new_celery:
            print(f"     PID {p.get('ProcessId')}: {(p.get('CommandLine') or '')[:80]}...")
    except Exception as e:
        print(f"   Note inspecting fresh processes: {e}")

    print("\nCelery fleet restart completed successfully.")


if __name__ == "__main__":
    restart_celery_fleet()
