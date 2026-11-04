"""Check live status of all orchestrator ports and services."""

import socket

SERVICES = [
    ("Frontend (Next.js)", "127.0.0.1", 3000),
    ("Backend API (FastAPI)", "127.0.0.1", 8000),
    ("Redis Queue Broker", "127.0.0.1", 6379),
    ("PostgreSQL Database", "127.0.0.1", 5432),
    ("MailDev SMTP", "127.0.0.1", 1025),
    ("MailDev Web UI", "127.0.0.1", 1080),
]

print("\n" + "=" * 55)
print("UAIC SYSTEM PORTS AND SERVICES LIVE AUDIT")
print("=" * 55)

for name, host, port in SERVICES:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((host, port))
    is_open = result == 0
    status = "LISTENING / ACTIVE" if is_open else "OFFLINE / NOT RUNNING"
    print(f"{name:<25} Port {port:>5} : {status}")
    sock.close()

print("=" * 55 + "\n")

