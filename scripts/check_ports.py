import socket

ports = [3000, 8000, 5555, 6379, 5432, 1080, 1025]
results = {}
for p in ports:
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(('127.0.0.1', p))
        results[p] = "OPEN"
        s.close()
    except Exception as e:
        results[p] = f"CLOSED ({e})"

for p, status in results.items():
    print(f"Port {p}: {status}")

