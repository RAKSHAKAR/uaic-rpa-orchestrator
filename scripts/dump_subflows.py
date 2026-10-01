import os
import re

subflows_dir = 'implementation_plan/v4_subflows'
files = [
    ('Broward', 'Subflow_Broward.robin'),
    ('Hillsborough', 'Subflow_Hillsborough.robin'),
    ('Miami', 'Subflow_Miami.robin'),
    ('Harris County Clerk', 'Subflow_Cclerk.robin'),
    ('Dallas', 'Subflow_Dallas.robin'),
    ('Harris JP', 'Subflow_Harris.robin'),
    ('Harris District', 'Subflow_HarrisDistrict.robin'),
    ('Travis', 'Subflow_Travis.robin'),
]

output_lines = []

for name, fname in files:
    path = os.path.join(subflows_dir, fname)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    output_lines.append("=" * 80)
    output_lines.append(f"SUBFLOW: {name} ({fname}) - {len(lines)} lines")
    output_lines.append("=" * 80)
    
    for idx, l in enumerate(lines):
        clean = l.strip()
        if not clean:
            continue
        # Check if line is WebAutomation, SET, Javascript, LOOP, etc.
        output_lines.append(f"{idx+1:03d}: {clean}")
    output_lines.append("")

with open('scripts/v4_all_8_subflows_annotated.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines))

print(f"Wrote {len(output_lines)} lines to scripts/v4_all_8_subflows_annotated.txt")
