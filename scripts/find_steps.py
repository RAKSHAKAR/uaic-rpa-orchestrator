import re

with open('frontend/src/app/settings/page.tsx', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if re.search(r'\bstep\b|\bsteps\b', line, re.IGNORECASE):
            # check if it's not an html attribute like step="0.1" or step="1"
            stripped = re.sub(r'step=["\']?[0-9.]+["\']?', '', line)
            if re.search(r'\bstep\b|\bsteps\b', stripped, re.IGNORECASE):
                print(f"{i}: {line.strip()}")
