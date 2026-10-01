import subprocess
import os
import sys
import json
import time

def get_processes():
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Select-Object ProcessId, CommandLine | ConvertTo-Json -Depth 2"],
        text=True
    )
    procs = json.loads(out)
    if isinstance(procs, dict):
        procs = [procs]
    return procs

def main():
    procs = get_processes()
    celery_worker_pids = []
    celery_beat_pids = []
    celery_flower_pids = []
    uvicorn_pids = []
    
    for p in procs:
        cmd = (p.get("CommandLine") or "").lower()
        pid = p.get("ProcessId")
        if "celery" in cmd:
            if "beat" in cmd:
                celery_beat_pids.append((pid, p.get("CommandLine")))
            elif "flower" in cmd:
                celery_flower_pids.append((pid, p.get("CommandLine")))
            else:
                celery_worker_pids.append((pid, p.get("CommandLine")))
        elif "uvicorn" in cmd:
            uvicorn_pids.append((pid, p.get("CommandLine")))

    print(f"Celery Workers: {len(celery_worker_pids)}")
    for pid, cmd in celery_worker_pids:
        print(f"  Worker PID {pid}: {cmd}")

    print(f"Celery Beat: {len(celery_beat_pids)}")
    for pid, cmd in celery_beat_pids:
        print(f"  Beat PID {pid}: {cmd}")

    print(f"Celery Flower: {len(celery_flower_pids)}")
    for pid, cmd in celery_flower_pids:
        print(f"  Flower PID {pid}: {cmd}")

    print(f"Uvicorn: {len(uvicorn_pids)}")
    for pid, cmd in uvicorn_pids:
        print(f"  Uvicorn PID {pid}: {cmd}")

if __name__ == "__main__":
    main()
