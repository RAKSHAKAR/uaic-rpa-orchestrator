"""
cleanup_legacy_docs.py - Safely remove consolidated redundant documentation files.
Verifies that master files, ChatGPT_Prompt, and protected files exist before deleting anything.
"""

import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMPL_DIR = os.path.join(REPO_ROOT, "implementation_plan")

# 1. Verification of Master Files
master_plan = os.path.join(IMPL_DIR, "2026-09-05_uaic_master-implementation-plan_v1.md")
master_gap = os.path.join(IMPL_DIR, "2026-09-05_uaic_master-gap-analysis_v1.md")
master_wt = os.path.join(IMPL_DIR, "2026-09-05_uaic_master-walkthrough_v1.md")
chatgpt_dir = os.path.join(IMPL_DIR, "ChatGPT_Prompt")

assert os.path.exists(master_plan), f"Missing {master_plan}"
assert os.path.exists(master_gap), f"Missing {master_gap}"
assert os.path.exists(master_wt), f"Missing {master_wt}"
assert os.path.exists(chatgpt_dir), f"Missing {chatgpt_dir}"

print("Master documents and ChatGPT_Prompt directory verified present.")

# 2. Identify redundant files to delete
files_to_delete = []

# Root implementation plans
for i in range(2, 11):
    fp = os.path.join(IMPL_DIR, f"implementation_plan_{i}.md")
    if os.path.exists(fp):
        files_to_delete.append(fp)

legacy_plan_1 = os.path.join(IMPL_DIR, "implementation_plan.md")
if os.path.exists(legacy_plan_1):
    files_to_delete.append(legacy_plan_1)

# New folder contents
new_folder = os.path.join(IMPL_DIR, "New folder")
if os.path.exists(new_folder):
    for f in os.listdir(new_folder):
        fp = os.path.join(new_folder, f)
        if os.path.isfile(fp):
            files_to_delete.append(fp)

print(f"Total legacy files scheduled for safe removal: {len(files_to_delete)}")
for f in files_to_delete:
    print(f"  Removing: {os.path.relpath(f, REPO_ROOT)}")
    os.remove(f)

# Remove empty New folder
if os.path.exists(new_folder) and len(os.listdir(new_folder)) == 0:
    print(f"  Removing empty folder: {os.path.relpath(new_folder, REPO_ROOT)}")
    os.rmdir(new_folder)

# Remove temp scratch text files in ai_current if present
ai_current = os.path.join(IMPL_DIR, "ai_current")
temp_scratch = ["_p1_master_impl.txt", "_p2_correction.txt", "_p3_uiux.txt", "_p4_python.txt", "_p5_courtcases.txt", "_prompt_temp.txt"]
for ts in temp_scratch:
    fp = os.path.join(ai_current, ts)
    if os.path.exists(fp):
        print(f"  Removing temp scratch: {os.path.relpath(fp, REPO_ROOT)}")
        os.remove(fp)

print("\nCleanup completed safely. Verifying remaining implementation_plan contents:")
for item in os.listdir(IMPL_DIR):
    print(f"  - {item}")
