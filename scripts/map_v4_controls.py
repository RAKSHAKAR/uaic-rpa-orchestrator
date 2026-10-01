import json
import glob
import os
import re

# Load all control repositories
repos = {}
for p in glob.glob('PowerAutomateSolutions/BotCreation_1_0_0_7/**/ControlRepository*.json', recursive=True):
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for s in data.get('Screens', []):
            s_name = s.get('Name', '')
            for c in s.get('Controls', []):
                c_name = c.get('Name', '')
                c_id = c.get('Id', '')
                tag = c.get('Tag', '')
                sels = c.get('Selectors', [])
                attr_parts = []
                for sel in sels:
                    for elem in sel.get('Elements', []):
                        e_tag = elem.get('Tag', '')
                        parts = []
                        for a in elem.get('Attributes', []):
                            if not a.get('Ignore', False):
                                parts.append(f"{a.get('Name')}='{a.get('Value')}'")
                        attr_parts.append(f"{e_tag}[{', '.join(parts)}]" if parts else e_tag)
                key = f"{s_name} > {c_name}"
                repos[key] = {
                    'screen': s_name,
                    'control': c_name,
                    'id': c_id,
                    'tag': tag,
                    'selector': " > ".join(attr_parts),
                    'raw': c
                }

print(f"Total controls mapped from all repos: {len(repos)}")

# Inspect subflows
subflows_dir = 'implementation_plan/v4_subflows'
for fname in sorted(os.listdir(subflows_dir)):
    if not fname.endswith('.robin') or fname.startswith('Subflow_Error') or fname.startswith('Subflow_Send'):
        continue
    path = os.path.join(subflows_dir, fname)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("=" * 80)
    print(f"SUBFLOW: {fname}")
    print("=" * 80)
    
    # Find all UIElement references
    ui_refs = re.findall(r"appmask:['\"]([^'\"]+)['\"]", content)
    for ref in set(ui_refs):
        # ref format: ScreenName.ControlName or similar
        parts = ref.split('.')
        matched = False
        for k, v in repos.items():
            if all(p in k for p in parts[-2:]):
                print(f"  UIElement [{ref}]:\n    Selector: {v['selector']}")
                matched = True
                break
        if not matched:
            print(f"  UIElement [{ref}]: (NOT DIRECTLY IN REPO OR CUSTOM MASK)")

    # Find JavaScript executions
    js_calls = re.findall(r"WebAutomation\.ExecuteJavascript.*?JavascriptCode:\s*([$']{1,3}.*?['$]{1,3})", content, re.DOTALL)
    if js_calls:
        print("\n  JavaScript Execution Calls:")
        for idx, j in enumerate(js_calls):
            # Clean up Robin string formatting
            clean_j = j.strip("$'\" \r\n")[:200]
            print(f"    [{idx+1}]: {clean_j}...")
