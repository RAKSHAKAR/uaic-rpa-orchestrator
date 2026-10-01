import json
import os

path = os.path.join(
    os.path.dirname(__file__),
    '..',
    'PowerAutomateSolutions',
    'BotCreation_1_0_0_7',
    'desktopflowbinaries',
    'b85f1bfd-d92b-4e25-ac23-a9e18e3d0606',
    'data',
    'ControlRepository_104c291e-5233-425c-bde4-e4db1c27a012.json'
)

if not os.path.exists(path):
    print("File not found:", path)
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("EXTRACTED POWER AUTOMATE V4 CONTROL REPOSITORY SELECTORS")
print("=" * 80)

for s in data.get('Screens', []):
    s_name = s.get('Name', '')
    for c in s.get('Controls', []):
        c_name = c.get('Name', '')
        tag = c.get('Tag', '')
        sels = c.get('Selectors', [])
        attr_parts = []
        for sel in sels:
            for elem in sel.get('Elements', []):
                e_tag = elem.get('Tag', '')
                for a in elem.get('Attributes', []):
                    if not a.get('Ignore', False):
                        attr_parts.append(f"{e_tag}[{a.get('Name')}='{a.get('Value')}']")
        print(f"[{s_name}] -> {c_name} (tag: {tag})")
        if attr_parts:
            print("    Selector:", " > ".join(attr_parts))
        print()
