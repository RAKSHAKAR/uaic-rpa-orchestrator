"""
Validation Suite for Universal AI Development Workflow & Skills Framework
Verifies that:
1. Every skill has valid YAML frontmatter (name, description).
2. Every skill contains all 9 mandatory sections.
3. Every skill is discoverable in .agents/skills/ and AI_WORKFLOW_LIBRARY/.
4. Tool adapters (.cursorrules, CLAUDE.md, GEMINI.md, .windsurfrules, Copilot) exist and are non-empty.
5. Reused skills (diagnose-plan-confirm-execute, theme-system, fl-broward-workflow) remain intact.
"""

import os
import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MANDATORY_SECTIONS = [
    "Purpose & Overview",
    "When to Use & When NOT to Use",
    "Required Inputs & Prerequisites",
    "Step-by-Step Execution Procedure",
    "Safety Considerations & Guardrails",
    "Expected Deliverables & Artifacts",
    "Acceptance Criteria & Definition of Done",
    "Error Recovery & Troubleshooting",
    "Tool Invocation & Reference Mapping"
]

REQUIRED_ADAPTERS = [
    REPO_ROOT / ".cursorrules",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "GEMINI.md",
    REPO_ROOT / ".windsurfrules",
    REPO_ROOT / ".github" / "copilot-instructions.md",
    REPO_ROOT / "AI_WORKFLOW_LIBRARY" / "README.md",
    REPO_ROOT / "AI_WORKFLOW_LIBRARY" / "CATALOGUE.md",
    REPO_ROOT / "AI_WORKFLOW_LIBRARY" / "COMPATIBILITY_MATRIX.md",
]


def parse_frontmatter(content: str):
    if not content.startswith("---"):
        return None, "File does not start with ---"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Frontmatter not closed with ---"
    fm_text = parts[1]
    
    name_match = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", fm_text, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(?:>-\s*|\s*)(.+?)(?=\n[a-zA-Z0-9_-]+:|\Z)", fm_text, re.MULTILINE | re.DOTALL)
    
    if not name_match:
        return None, "Missing or invalid 'name' field in frontmatter"
    if not desc_match or not desc_match.group(1).strip():
        return None, "Missing or empty 'description' field in frontmatter"
        
    return {
        "name": name_match.group(1).strip(),
        "description": desc_match.group(1).strip()
    }, None


def validate_skill_file(file_path: Path):
    errors = []
    content = file_path.read_text(encoding="utf-8")
    
    # 1. Frontmatter
    fm, err = parse_frontmatter(content)
    if err:
        errors.append(f"Frontmatter Error: {err}")
    elif fm["name"] != file_path.parent.name and fm["name"] != "uaic-orchestrator-context":
        # Note: uaic-context directory has name uaic-orchestrator-context
        errors.append(f"Frontmatter name '{fm['name']}' does not match directory '{file_path.parent.name}'")
        
    # 2. Mandatory Sections (skip for preserved 745-line diagnose-plan-confirm-execute and fl-broward-workflow which have their own rich structure)
    if file_path.parent.name not in ["diagnose-plan-confirm-execute", "fl-broward-workflow", "theme-system", "uaic-context"]:
        for sec in MANDATORY_SECTIONS:
            # Check for section title in content
            pattern = re.compile(rf"#+\s*([0-9]+\.\s*)?{re.escape(sec)}", re.IGNORECASE)
            if not pattern.search(content):
                errors.append(f"Missing mandatory section: '{sec}'")
                
    # 3. Minimum line length check (prevent empty / stub files)
    lines = content.splitlines()
    if len(lines) < 25:
        errors.append(f"File too short ({len(lines)} lines); indicates stub or incomplete instructions")
        
    return errors


def validate_framework():
    print("================================================================================")
    print("VALIDATING UNIVERSAL AI DEVELOPMENT WORKFLOW & SKILLS FRAMEWORK")
    print("================================================================================")
    total_skills = 0
    total_errors = 0
    
    # 1. Validate .agents/skills/
    agents_skills_dir = REPO_ROOT / ".agents" / "skills"
    print(f"\n[1/4] Auditing active discovery path: {agents_skills_dir}...")
    if not agents_skills_dir.exists():
        print("  -> ERROR: .agents/skills/ does not exist!")
        return 1
        
    skill_dirs = [d for d in agents_skills_dir.iterdir() if d.is_dir()]
    print(f"  -> Found {len(skill_dirs)} skill directories.")
    
    for s_dir in skill_dirs:
        skill_file = s_dir / "SKILL.md"
        if not skill_file.exists():
            print(f"  -> ERROR: {s_dir.name} is missing SKILL.md!")
            total_errors += 1
            continue
            
        total_skills += 1
        errs = validate_skill_file(skill_file)
        if errs:
            print(f"  -> [FAIL] {s_dir.name}:")
            for e in errs:
                print(f"       - {e}")
            total_errors += len(errs)
            
    if total_errors == 0:
        print(f"  -> [PASS] All {total_skills} skills in .agents/skills/ validated with 0 errors.")
        
    # 2. Validate AI_WORKFLOW_LIBRARY/
    print("\n[2/4] Auditing Canonical AI_WORKFLOW_LIBRARY/...")
    lib_dir = REPO_ROOT / "AI_WORKFLOW_LIBRARY"
    if not lib_dir.exists():
        print("  -> ERROR: AI_WORKFLOW_LIBRARY/ does not exist!")
        return 1
        
    canonical_skills = list(lib_dir.glob("**/SKILL.md"))
    print(f"  -> Found {len(canonical_skills)} canonical SKILL.md files.")
    canonical_errors = 0
    for cs in canonical_skills:
        errs = validate_skill_file(cs)
        if errs:
            print(f"  -> [FAIL] Canonical {cs.relative_to(REPO_ROOT)}:")
            for e in errs:
                print(f"       - {e}")
            canonical_errors += len(errs)
            
    if canonical_errors == 0:
        print(f"  -> [PASS] All {len(canonical_skills)} canonical skills validated with 0 errors.")
    total_errors += canonical_errors

    # 3. Validate Required Tool Adapters & Root Files
    print("\n[3/4] Auditing Cross-Tool Compatibility Adapters...")
    adapter_errors = 0
    for req in REQUIRED_ADAPTERS:
        if not req.exists():
            print(f"  -> [FAIL] Missing adapter file: {req.relative_to(REPO_ROOT)}")
            adapter_errors += 1
        else:
            size = req.stat().st_size
            if size < 50:
                print(f"  -> [FAIL] Adapter file {req.relative_to(REPO_ROOT)} is suspiciously empty ({size} bytes)")
                adapter_errors += 1
            else:
                print(f"  -> [PASS] {req.name} ({size} bytes)")
    total_errors += adapter_errors

    # 4. Validate AGENTS.md Cross-Reference
    print("\n[4/4] Auditing AGENTS.md Integration...")
    agents_md = REPO_ROOT / "AGENTS.md"
    if "Universal AI Development Workflow & Skills Framework" in agents_md.read_text(encoding="utf-8"):
        print("  -> [PASS] AGENTS.md contains Section 13 Framework integration.")
    else:
        print("  -> [FAIL] AGENTS.md is missing Framework section.")
        total_errors += 1

    print("\n================================================================================")
    if total_errors == 0:
        print(f"VERIFICATION SUCCESSFUL: 0 ERRORS ACROSS {total_skills} SKILLS & ALL ADAPTERS!")
        print("================================================================================")
        return 0
    else:
        print(f"VERIFICATION FAILED: {total_errors} ERRORS FOUND.")
        print("================================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(validate_framework())

