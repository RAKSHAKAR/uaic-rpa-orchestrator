import json
import re
import os

path = 'PowerAutomateSolutions/BotCreation_1_0_0_7/Workflows/UAICBotCreationMainFlow-V4-01092026-67DD091D-0AB9-4099-97AF-47136F16CE4A.json'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    text = json.dumps(data)
    urls = re.findall(r'https?://[^\s"\'\\]+', text)
    print("Found URLs in V4 workflow JSON:")
    for u in sorted(set(urls)):
        print("  -", u)

print("\n--- Subflows in implementation_plan/v4_subflows ---")
subflow_dir = 'implementation_plan/v4_subflows'
for sf in sorted(os.listdir(subflow_dir)):
    p = os.path.join(subflow_dir, sf)
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"\nSubflow: {sf}")
    for idx, l in enumerate(lines, 1):
        if any(k in l for k in ['LaunchChrome', 'GoToWebPage', 'CreateNewTab', 'http://', 'https://']):
            print(f"  Line {idx:03d}: {l.strip()}")
