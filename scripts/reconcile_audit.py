"""
reconcile_audit.py - Forensic analysis script for UAIC documentation reconciliation.
Reads all ChatGPT prompt files, legacy implementation plans, gap analyses, and walkthroughs.
Extracts structured topics, requirements, and cross-references them.
"""

import os
import sys
import glob
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

print(f"Analyzing from REPO_ROOT: {REPO_ROOT}")

# 1. Inspect ChatGPT prompts
prompt_files = {
    "P1_MASTER": os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p1_master_impl.txt"),
    "P2_CORRECTION": os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p2_correction.txt"),
    "P3_UIUX": os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p3_uiux.txt"),
    "P4_PYTHON": os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p4_python.txt"),
    "P5_COURTCASES": os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_p5_courtcases.txt"),
    "P0_RECONCILIATION": os.path.join(REPO_ROOT, "implementation_plan", "ai_current", "_prompt_temp.txt"),
}

prompt_stats = {}
for name, p in prompt_files.items():
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.splitlines()
            headings = [line.strip() for line in lines if line.strip().startswith("#")]
            prompt_stats[name] = {
                "lines": len(lines),
                "chars": len(content),
                "headings": len(headings),
                "heading_list": headings
            }
            print(f"Loaded {name}: {len(lines)} lines, {len(content)} chars, {len(headings)} headings")

# 2. Inspect historical plans
plans_root = glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "implementation_plan*.md"))
plans_new_folder = glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "New folder", "implementation_plan*.md"))
all_plans = sorted(plans_root + plans_new_folder)
print(f"\nTotal historical implementation plans found: {len(all_plans)}")

gap_files = sorted(glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "New folder", "gap_analysis*.md")))
print(f"Total historical gap analyses found: {len(gap_files)}")

walkthrough_files = sorted(glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "New folder", "walkthrough*.md")) + 
                           glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "New folder", "walkthrough_*")))
print(f"Total historical walkthroughs found: {len(walkthrough_files)}")

# 3. Read and summarize each group
def analyze_files(file_list, category):
    results = []
    for fp in file_list:
        fname = os.path.basename(fp)
        size = os.path.getsize(fp)
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        headers = [l.strip() for l in lines if l.strip().startswith("#")]
        results.append({
            "file": fname,
            "path": fp,
            "size": size,
            "lines": len(lines),
            "headers": headers
        })
    return results

plan_data = analyze_files(all_plans, "plans")
gap_data = analyze_files(gap_files, "gaps")
wt_data = analyze_files(walkthrough_files, "walkthroughs")

print("\n--- SUMMARY OF HISTORICAL PLANS ---")
for p in plan_data:
    title = p['headers'][0] if p['headers'] else 'No title'
    print(f"{p['file']} ({p['size']} bytes, {p['lines']} lines): {title[:80]}")

print("\n--- SUMMARY OF GAP ANALYSES ---")
for g in gap_data:
    title = g['headers'][0] if g['headers'] else 'No title'
    print(f"{g['file']} ({g['size']} bytes, {g['lines']} lines): {title[:80]}")

print("\n--- SUMMARY OF WALKTHROUGHS ---")
for w in wt_data:
    title = w['headers'][0] if w['headers'] else 'No title'
    print(f"{w['file']} ({w['size']} bytes, {w['lines']} lines): {title[:80]}")
