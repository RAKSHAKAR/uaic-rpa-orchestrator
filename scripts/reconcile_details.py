"""
reconcile_details.py - Read every implementation plan, gap analysis, and walkthrough
and produce a detailed breakdown of what each document addressed.
"""

import os
import sys
import glob
import re

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_doc_summary(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    lines = content.splitlines()
    title = lines[0] if lines else ""
    
    # Extract headings (h1, h2)
    headings = [l.strip() for l in lines if l.startswith("# ") or l.startswith("## ")]
    
    # Extract sections like Problem, Solution, Decisions, Results, Files Modified
    problem_m = re.search(r'## (?:Problem|Objective|Background|Context|User Review)(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
    problem = problem_m.group(1).strip()[:300].replace("\n", " ") if problem_m else ""
    
    # Extract file paths mentioned
    files_mentioned = set(re.findall(r'[`"]([a-zA-Z0-9_\-\.\/\\]+\.(?:py|tsx|ts|js|json|css|html|md|ps1|yml|yaml))[`"]', content))
    
    return {
        "file": os.path.basename(file_path),
        "title": title,
        "headings": headings[:10],
        "total_headings": len(headings),
        "problem_snippet": problem,
        "files_mentioned": sorted(list(files_mentioned))[:15],
        "size": len(content),
        "lines": len(lines)
    }

# Historical plans
plans = sorted(glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "implementation_plan*.md")) +
               glob.glob(os.path.join(REPO_ROOT, "implementation_plan", "New folder", "implementation_plan*.md")))

print(f"=== DETAILED SUMMARY OF {len(plans)} HISTORICAL PLANS ===")
for p in plans:
    s = get_doc_summary(p)
    print(f"\n--- {s['file']} ({s['lines']} lines) ---")
    print(f"  Title: {s['title']}")
    print(f"  Headings: {', '.join([h.replace('#', '').strip() for h in s['headings'][:5]])}")
    if s['problem_snippet']:
        print(f"  Summary: {s['problem_snippet'][:180]}...")
    print(f"  Files referenced: {', '.join(s['files_mentioned'][:8])}")

