import glob
import re

for f in glob.glob('**/*.robin', recursive=True):
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()
    matches = re.findall(r"WebAutomation\.LaunchChrome[^\r\n]+", content)
    if matches:
        print(f"\n--- {f} ---")
        for m in matches:
            print("  ", m)
