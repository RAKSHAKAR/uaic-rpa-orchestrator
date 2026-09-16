import os

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

in_automation = False
for i, l in enumerate(lines):
    if '{activeTab === "automation"' in l:
        in_automation = True
        print(f"Automation start: Line {i+1}")
    elif in_automation and '{activeTab ===' in l:
        print(f"Automation end: Line {i+1}")
        break
    elif in_automation:
        # print major divs/headings
        if '<h3' in l or '<h4' in l or '<label' in l:
            text = l.strip()
            print(f"  Line {i+1}: {text[:90]}")
