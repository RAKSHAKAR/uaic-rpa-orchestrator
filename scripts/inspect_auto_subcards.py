import os

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

automation_lines = lines[1996:3129]

# Let's see all subcards and sections
for idx, line in enumerate(automation_lines):
    actual_line = 1997 + idx
    if any(k in line for k in ['<h3', '<h4', 'border-b', 'font-bold', '/*']):
        print(f"{actual_line}: {line.strip()[:100]}")
