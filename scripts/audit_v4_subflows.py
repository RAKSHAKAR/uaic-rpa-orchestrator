import os
import re

subflows_dir = os.path.join(os.path.dirname(__file__), '..', 'implementation_plan', 'v4_subflows')

subflow_files = {
    'Broward': 'Subflow_Broward.robin',
    'Hillsborough': 'Subflow_Hillsborough.robin',
    'Miami': 'Subflow_Miami.robin',
    'Harris County Clerk': 'Subflow_Cclerk.robin',
    'Dallas': 'Subflow_Dallas.robin',
    'Harris JP': 'Subflow_Harris.robin',
    'Harris District': 'Subflow_HarrisDistrict.robin',
    'Travis': 'Subflow_Travis.robin',
}

print("=" * 80)
print("AUDITING ALL 8 POWER AUTOMATE V4 SUBFLOWS")
print("=" * 80)

for name, fname in subflow_files.items():
    path = os.path.join(subflows_dir, fname)
    if not os.path.exists(path):
        print(f"MISSING: {name} ({fname})")
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print(f"\n--- {name.upper()} ({fname}) --- ({len(content.splitlines())} lines)")
    
    # URLs
    urls = re.findall(r"Url:\s*[$']+'?([^'\r\n]+)", content)
    if urls:
        print(f"  URLs referenced: {urls}")
    
    # WebAutomation actions
    actions = re.findall(r"(WebAutomation\.[A-Za-z0-9_.]+)", content)
    action_counts = {}
    for a in actions:
        action_counts[a] = action_counts.get(a, 0) + 1
    print("  Actions used:")
    for a, c in sorted(action_counts.items()):
        print(f"    {a}: {c}")

    # UI Elements referenced
    elements = re.findall(r"UIElement:\s*(appmask:[^\r\n]+)", content)
    if elements:
        print(f"  UIElements referenced ({len(elements)}):")
        for e in set(elements):
            print(f"    {e}")

