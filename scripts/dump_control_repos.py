import json
import glob

output = []
for p in glob.glob('PowerAutomateSolutions/BotCreation_1_0_0_7/**/ControlRepository*.json', recursive=True):
    output.append("=" * 80)
    output.append(f"FILE: {p}")
    output.append("=" * 80)
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for s in data.get('Screens', []):
        s_name = s.get('Name', '')
        output.append(f"\nSCREEN: {s_name}")
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
            output.append(f"  CONTROL: {c_name} (tag: {tag}, id: {c_id})")
            if attr_parts:
                output.append(f"    SELECTOR: {' > '.join(attr_parts)}")

with open('scripts/v4_all_control_repositories.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output))

print(f"Wrote {len(output)} lines to scripts/v4_all_control_repositories.txt")
