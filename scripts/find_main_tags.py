import os
import re

app_dir = "frontend/src/app"
for root, dirs, files in os.walk(app_dir):
    for f in files:
        if f.endswith(".tsx"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                matches = re.findall(r'<main[^>]*>', content)
                for m in matches:
                    rel = os.path.relpath(path, app_dir)
                    print(f"{rel}: {m[:100]}")
