"""
Mermaid Syntax & Quality Validator for UAIC Orchestrator Documentation
Ensures all Mermaid diagrams render cleanly without errors across all Markdown parsers,
support both Light and Dark modes with professional contrast, and prevent future regressions.
"""
import os
import re
import sys

def check_mermaid_syntax(root_dir='.'):
    total_files_checked = 0
    total_blocks_checked = 0
    errors = []

    for root, dirs, files in os.walk(root_dir):
        if any(p in root for p in ['.git', 'node_modules', '.venv', '.gemini', '__pycache__']):
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                total_files_checked += 1
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if '```mermaid' in content:
                        blocks = re.findall(r'```mermaid(.*?)```', content, re.DOTALL)
                        for idx, b in enumerate(blocks, 1):
                            total_blocks_checked += 1
                            lines = [l.strip() for l in b.strip().splitlines() if l.strip()]
                            first_line = lines[0] if lines else ""

                            # Rule 1: No corrupt/non-ASCII replacement characters
                            if '\ufffd' in b:
                                errors.append(f"{path} Block {idx}: contains replacement character (corrupted text)")

                            # Rule 2: No HTML tags
                            if re.search(r'<br\s*/?>|<font|<b>|<i>|<div>', b, re.IGNORECASE):
                                errors.append(f"{path} Block {idx}: contains HTML tags")

                            # Rule 3: No unquoted arrows in labels
                            unquoted_arrows = re.findall(r'\[([^\]\n]*->[^\]\n]*)\]', b)
                            for ua in unquoted_arrows:
                                if not (ua.startswith('"') and ua.endswith('"')):
                                    errors.append(f"{path} Block {idx}: unquoted arrow in label: [{ua}]")

                            # Rule 4: No '&' chaining syntax
                            if re.search(r'\w+\s*&\s*\w+\s*-->', b):
                                errors.append(f"{path} Block {idx}: contains '&' chaining syntax")

                            # Rules for flowcharts & graphs
                            if first_line.startswith('flowchart') or first_line.startswith('graph'):
                                # Rule 5: Must contain classDef for professional contrast & theme compatibility
                                if 'classDef' not in b:
                                    errors.append(f"{path} Block {idx}: missing 'classDef' styling (risk of dark mode invisibility)")

                                # Rule 6: No direction TB/LR inside subgraphs (breaks older/bundled mermaid engines)
                                if re.search(r'subgraph[\s\S]*?direction\s+(TB|TD|LR|RL)[\s\S]*?end', b):
                                    errors.append(f"{path} Block {idx}: contains 'direction' inside subgraph (parser collision risk)")

                                # Rule 7: No direct subgraph-to-subgraph linking
                                subgraphs = set(re.findall(r'subgraph\s+([A-Za-z0-9_]+)', b))
                                for sg in subgraphs:
                                    if re.search(rf'{sg}\s*-->\s*\w+', b):
                                        # check if target is also a subgraph
                                        m = re.search(rf'{sg}\s*-->\s*(\w+)', b)
                                        if m and m.group(1) in subgraphs:
                                            errors.append(f"{path} Block {idx}: direct subgraph linking '{sg} --> {m.group(1)}' (parser collision risk)")

                except Exception as e:
                    errors.append(f"{path}: Failed to read ({e})")

    print(f"Mermaid Syntax & Quality Validation Summary:")
    print(f"  Markdown files inspected : {total_files_checked}")
    print(f"  Mermaid diagrams checked : {total_blocks_checked}")
    print(f"  Violations found         : {len(errors)}")

    if errors:
        print("\nERRORS DETECTED:")
        for err in errors:
            print(f"  [X] {err}")
        return False
    else:
        print("  [PASS] All Mermaid diagrams conform to strict rendering & quality standards.")
        return True

if __name__ == '__main__':
    success = check_mermaid_syntax()
    sys.exit(0 if success else 1)
