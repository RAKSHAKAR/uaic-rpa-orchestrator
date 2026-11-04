import glob
import re

files = glob.glob('**/*.md', recursive=True)

for path in files:
    try:
        content = open(path, 'r', encoding='utf-8').read()
    except Exception:
        continue
    blocks = list(re.finditer(r'```mermaid\s*\n(.*?)\n```', content, re.DOTALL))
    if not blocks:
        continue
    for b_idx, b in enumerate(blocks):
        text = b.group(1).strip()
        first_line = text.split('\n')[0]
        # Check issues:
        issues = []
        # Check subgraphs
        for m in re.finditer(r'subgraph\s+([^\n\[]+)', text):
            sg_name = m.group(1).strip()
            if ' ' in sg_name and not sg_name.startswith('"'):
                issues.append(f"Subgraph with spaces not formatted: '{sg_name}'")
        # Check unquoted labels with special chars
        for line in text.split('\n'):
            for m in re.finditer(r'(\w+)\s*(\[|\{|\(\[|\[\(|\(\()([^"\]\}\)]+)(\]|\}|\)\]|\)\]|\)\))', line):
                node_id, open_b, lbl, close_b = m.groups()
                if any(c in lbl for c in [':', '/', '+', '(', ')', '&', '?', '%', '->', '<', '>']):
                    issues.append(f"Unquoted label with special chars: {node_id}{open_b}{lbl}{close_b}")
            # Check unquoted link text with special chars
            for m in re.finditer(r'-->\|([^"\|]+)\|', line):
                link_lbl = m.group(1)
                if any(c in link_lbl for c in [':', '/', '+', '(', ')', '&', '?', '%', '->', '<', '>']):
                    issues.append(f"Unquoted link label with special chars: |{link_lbl}|")
        if issues:
            print(f"\nFILE: {path} (Block {b_idx+1}: {first_line})")
            for iss in issues[:10]:
                print(f"  * {iss}")
