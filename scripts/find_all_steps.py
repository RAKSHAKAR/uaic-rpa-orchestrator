import os
import re

for root, dirs, files in os.walk('frontend/src'):
    for f in files:
        if f.endswith(('.tsx', '.ts')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                for idx, line in enumerate(file, 1):
                    # Check for "Step 1", "Step 2", "Step:", "Step [0-9]"
                    if re.search(r'\bStep\s*\d+\b', line, re.IGNORECASE):
                        print(f"{path}:{idx}: {line.strip()}")
