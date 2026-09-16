import os
import re

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# Check all settings.* references
settings_refs = set(re.findall(r'settings\.([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)?)', code))
print("Settings properties accessed in UI:")
for r in sorted(settings_refs):
    print(f"  settings.{r}")

# Check all handler functions defined in page.tsx
handlers = re.findall(r'const\s+(handle[A-Za-z0-9_]+|test[A-Za-z0-9_]+)\s*=', code)
print("\nKey Handlers:")
for h in sorted(set(handlers)):
    print(f"  {h}")
