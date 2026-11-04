import os
import re

files_with_mermaid = []
for root, dirs, files in os.walk('.'):
    if any(skip in root for skip in ['.venv', 'node_modules', '.git']):
        continue
    for f in files:
        if f.endswith('.md'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                blocks = re.findall(r'```mermaid(.*?)```', content, re.DOTALL)
                if blocks:
                    files_with_mermaid.append((p, blocks))

print(f"Total files with mermaid: {len(files_with_mermaid)}")
total_blocks = sum(len(b) for _, b in files_with_mermaid)
print(f"Total mermaid blocks: {total_blocks}")

for p, blocks in files_with_mermaid:
    print(f"\nFile: {p} ({len(blocks)} blocks)")
    for idx, b in enumerate(blocks):
        has_classdef = 'classDef' in b
        has_subgraph = 'subgraph' in b
        has_style = 'style ' in b
        print(f"  Block {idx+1}: classDef={has_classdef}, subgraph={has_subgraph}, style={has_style}, lines={len(b.strip().splitlines())}")
