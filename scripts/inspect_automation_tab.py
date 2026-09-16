import os

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

line_nums = [2000, 2130, 2525, 2600, 2730, 2815, 2865, 2935]
for start in line_nums:
    print(f"\n--- Around Line {start} ---")
    for idx in range(start-1, min(start+20, len(lines))):
        print(f"{idx+1}: {lines[idx].strip()[:110]}")
