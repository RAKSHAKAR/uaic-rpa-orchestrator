import os

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

def find_line(pattern):
    for i, l in enumerate(lines):
        if pattern in l:
            return i + 1
    return None

print("guidewire start:", find_line('{activeTab === "guidewire"'))
print("portals start:", find_line('{activeTab === "portals"'))
print("automation start:", find_line('{activeTab === "automation"'))
print("proxy start:", find_line('{activeTab === "proxy"'))
print("extension start:", find_line('{activeTab === "extension"'))
print("email start:", find_line('{activeTab === "email"'))
print("storage start:", find_line('{activeTab === "storage"'))
print("matcher start:", find_line('{activeTab === "matcher"'))
print("queue start:", find_line('{activeTab === "queue"'))
