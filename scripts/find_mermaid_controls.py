import os
import glob
import re

ext_path = glob.glob(os.path.expanduser('~/.vscode/extensions/bierner.markdown-mermaid*'))[0]
bundle_path = os.path.join(ext_path, 'dist-preview', 'index.bundle.js')

with open(bundle_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# find zoom or controls logic
matches = [m.start() for m in re.finditer(r'markdown-mermaid', text)]
print(f"Found {len(matches)} occurrences of 'markdown-mermaid'")
for pos in matches[:5]:
    print("---")
    print(text[max(0, pos-100):min(len(text), pos+200)])
