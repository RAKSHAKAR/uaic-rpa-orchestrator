"""
reconcile_all_requirements.py - Extract all requirements from P1-P5 and check code status.
"""

import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def parse_prompt(file_path, prefix):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Split by markdown headers (# or ##)
    sections = re.split(r'\n(?=#{1,3}\s+)', content)
    reqs = []
    for sec in sections:
        lines = sec.strip().splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        
        # Check if header is a section or numbered item
        m = re.match(r'#{1,3}\s+(?:(\d+)[\.\s]+)?(.*)', header)
        if m:
            num = m.group(1) or ""
            title = m.group(2).strip()
            req_id = f"{prefix}-{num}" if num else f"{prefix}-{len(reqs)+1}"
            reqs.append({
                "id": req_id,
                "header": header,
                "title": title,
                "body_len": len(body),
                "snippet": body[:200].replace("\n", " ")
            })
    return reqs

p1_reqs = parse_prompt(os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p1_master_impl.txt"), "P1")
p2_reqs = parse_prompt(os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p2_correction.txt"), "P2")
p3_reqs = parse_prompt(os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p3_uiux.txt"), "P3")
p4_reqs = parse_prompt(os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p4_python.txt"), "P4")
p5_reqs = parse_prompt(os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p5_courtcases.txt"), "P5")

print(f"P1 (Master Implementation 1): {len(p1_reqs)} sections")
print(f"P2 (Correction & Production): {len(p2_reqs)} sections")
print(f"P3 (UI/UX Responsive):        {len(p3_reqs)} sections")
print(f"P4 (Python 3.14 Runtime):     {len(p4_reqs)} sections")
print(f"P5 (Scraped Court Cases & GW):{len(p5_reqs)} sections")
print(f"Total prompt sections to reconcile: {len(p1_reqs) + len(p2_reqs) + len(p3_reqs) + len(p4_reqs) + len(p5_reqs)}")

# Sample output of P1
print("\n--- SAMPLE P1 HEADINGS ---")
for r in p1_reqs[:15]:
    print(f"  {r['id']}: {r['title']}")

print("\n--- SAMPLE P2 HEADINGS ---")
for r in p2_reqs[:15]:
    print(f"  {r['id']}: {r['title']}")

print("\n--- SAMPLE P3 HEADINGS ---")
for r in p3_reqs[:15]:
    print(f"  {r['id']}: {r['title']}")

print("\n--- SAMPLE P4 HEADINGS ---")
for r in p4_reqs[:15]:
    print(f"  {r['id']}: {r['title']}")

print("\n--- SAMPLE P5 HEADINGS ---")
for r in p5_reqs[:15]:
    print(f"  {r['id']}: {r['title']}")
