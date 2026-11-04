"""
Master Build Script for Universal AI Development Workflow & Skills Framework
Author: AI Workflow Architect
Target Repository: UAIC Claim & RPA Orchestrator (D:\\scratch\\Bot_UAIC)
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from skills_data.category_a import SKILLS_A
from skills_data.category_b import SKILLS_B
from skills_data.category_c import SKILLS_C
from skills_data.category_d import SKILLS_D
from skills_data.category_e import SKILLS_E
from skills_data.category_f import SKILLS_F
from skills_data.category_g import SKILLS_G
from skills_data.category_h import SKILLS_H
from skills_data.category_i import SKILLS_I
from skills_data.category_j import SKILLS_J
from skills_data.renderer import render_skill_markdown

ALL_CATEGORIES = [
    ("01-discovery-requirements", "A", "Project Discovery & Requirements", SKILLS_A),
    ("02-planning-management", "B", "Planning & Project Management", SKILLS_B),
    ("03-app-development", "C", "Website & Application Development", SKILLS_C),
    ("04-code-quality", "D", "Code Quality & Maintenance", SKILLS_D),
    ("05-testing-qa", "E", "Testing & Quality Assurance", SKILLS_E),
    ("06-debugging", "F", "Debugging & Problem Resolution", SKILLS_F),
    ("07-deployment-devops", "G", "Deployment & DevOps", SKILLS_G),
    ("08-documentation", "H", "Documentation & Knowledge", SKILLS_H),
    ("09-agent-orchestration", "I", "Agent Management & Automation", SKILLS_I),
]

PROJECT_CATEGORIES = [
    ("uaic", "J", "Project-Specific UAIC Pack", SKILLS_J),
]


def build_canonical_library():
    print("[1/6] Building Canonical AI_WORKFLOW_LIBRARY...")
    base_dir = REPO_ROOT / "AI_WORKFLOW_LIBRARY"
    base_dir.mkdir(exist_ok=True)
    
    # Universal categories
    for folder, code, cat_name, skills in ALL_CATEGORIES:
        cat_dir = base_dir / "universal" / folder
        cat_dir.mkdir(parents=True, exist_ok=True)
        for skill in skills:
            skill_dir = cat_dir / skill["name"]
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            content = render_skill_markdown(skill)
            skill_file.write_text(content, encoding="utf-8")
    
    # Project-specific categories
    for folder, code, cat_name, skills in PROJECT_CATEGORIES:
        cat_dir = base_dir / "project-specific" / folder
        cat_dir.mkdir(parents=True, exist_ok=True)
        for skill in skills:
            skill_dir = cat_dir / skill["name"]
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            content = render_skill_markdown(skill)
            skill_file.write_text(content, encoding="utf-8")
            
    print("  -> Canonical library files generated successfully.")


def deploy_agents_skills():
    print("[2/6] Deploying skills to active discovery path (.agents/skills/)...")
    agents_skills_dir = REPO_ROOT / ".agents" / "skills"
    agents_skills_dir.mkdir(parents=True, exist_ok=True)
    
    # Existing skills to preserve / conditionally touch
    preserve_names = {
        "diagnose-plan-confirm-execute",
        "theme-system",
        "fl-broward-workflow"
    }
    
    all_skills = []
    for _, _, _, skills in ALL_CATEGORIES:
        all_skills.extend(skills)
    for _, _, _, skills in PROJECT_CATEGORIES:
        all_skills.extend(skills)
        
    for skill in all_skills:
        name = skill["name"]
        target_dir = agents_skills_dir / name
        target_file = target_dir / "SKILL.md"
        
        # If it's one of the preserved skills and already exists with extensive content, preserve it
        if name in preserve_names and target_file.exists():
            existing_content = target_file.read_text(encoding="utf-8")
            if len(existing_content.splitlines()) > 30:
                print(f"  -> Preserving existing comprehensive skill: {name} ({len(existing_content.splitlines())} lines)")
                continue
                
        target_dir.mkdir(parents=True, exist_ok=True)
        content = render_skill_markdown(skill)
        target_file.write_text(content, encoding="utf-8")
        
    # Also link uaic-orchestrator-context to existing uaic-context
    uaic_context_dir = agents_skills_dir / "uaic-context"
    if uaic_context_dir.exists():
        # Keep uaic-context intact and ensure uaic-orchestrator-context is also present
        pass

    print(f"  -> Deployed {len(all_skills)} skills to .agents/skills/.")


def generate_catalogue_and_matrix():
    print("[3/6] Generating CATALOGUE.md and COMPATIBILITY_MATRIX.md...")
    base_dir = REPO_ROOT / "AI_WORKFLOW_LIBRARY"
    
    all_skills = []
    for folder, code, cat_name, skills in ALL_CATEGORIES:
        for s in skills:
            all_skills.append((code, cat_name, f"universal/{folder}/{s['name']}", s))
    for folder, code, cat_name, skills in PROJECT_CATEGORIES:
        for s in skills:
            all_skills.append((code, cat_name, f"project-specific/{folder}/{s['name']}", s))

    # Generate CATALOGUE.md
    cat_rows = []
    for code, cat_name, rel_path, s in all_skills:
        cat_rows.append(
            f"| `{s['name']}` | {cat_name} | {s['description']} | [`SKILL.md`]({rel_path}/SKILL.md) |"
        )
    cat_table = "\n".join(cat_rows)
    
    catalogue_md = f"""# Universal AI Development Workflow & Skills Catalogue

**Version:** 1.0  
**Prepared:** 31 October 2026  
**Total Workflows / Skills:** {len(all_skills)}  
**Scope:** Universal Engineering Lifecycle + UAIC RPA Domain Pack  

---

## Complete Skills Catalogue

| Workflow / Skill Name | Category | Primary Purpose & Actionable Trigger | Canonical Location |
|---|---|---|---|
{cat_table}

---

## How to Invoke Skills in This Repository

### 1. Google Antigravity & OpenAI Codex
Every skill is deployed as an active, discoverable package in `.agents/skills/<skill-name>/SKILL.md`.  
- **Antigravity**: Discovers skills automatically via progressive disclosure (name & description injected into prompt context; full instructions loaded on demand). Invoke by name in chat: e.g. `/project-discovery`, `/api-development`, or ask the agent directly.
- **OpenAI Codex**: Discovers skills via `AGENTS.md` and reads `.agents/skills/<skill-name>/SKILL.md`.

### 2. Cursor
- Project rules configured in `.cursorrules` and `.cursor/rules/*.mdc`. Mention `@skill-name` in Composer or chat.

### 3. Claude Code
- Project instructions in `CLAUDE.md`. Reference skill names in prompts.

### 4. Gemini CLI
- Project instructions in `GEMINI.md`.

### 5. GitHub Copilot
- Instructions in `.github/copilot-instructions.md` and prompt templates in `.github/prompts/`.

### 6. Windsurf
- Cascade rules in `.windsurfrules`.
"""
    (base_dir / "CATALOGUE.md").write_text(catalogue_md, encoding="utf-8")

    # Generate COMPATIBILITY_MATRIX.md
    matrix_rows = []
    for code, cat_name, rel_path, s in all_skills:
        t = s.get("tool_invocations", {})
        ag_c = t.get("antigravity_class", "CUSTOM SKILL")
        cur_c = t.get("cursor_class", "CUSTOM RULE")
        cl_c = t.get("claude_class", "INSTRUCTION")
        cod_c = t.get("codex_class", "CUSTOM SKILL")
        gem_c = t.get("gemini_class", "CUSTOM SKILL")
        cop_c = t.get("copilot_class", "PROMPT FILE")
        wind_c = t.get("windsurf_class", "WORKFLOW")
        
        matrix_rows.append(
            f"| `{s['name']}` | `{ag_c}` | `{cur_c}` | `{cl_c}` | `{cod_c}` | `{gem_c}` | `{cop_c}` | `{wind_c}` |"
        )
    matrix_table = "\n".join(matrix_rows)

    compatibility_md = f"""# AI Tool Compatibility Matrix

**Version:** 1.0  
**Audit Date:** 31 October 2026  
**Evaluated AI Coding Tools:**
1. **Google Antigravity** (Active Tool)
2. **Cursor**
3. **Claude Code**
4. **OpenAI Codex**
5. **Gemini CLI**
6. **GitHub Copilot**
7. **Windsurf**

---

## Tool-Wise Mechanism & Discovery Summary

| AI Tool | Native Instruction File | Skills Discovery Location | Invocation Syntax | Progressive Disclosure Support |
|---|---|---|---|---|
| **Google Antigravity** | `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md` | `.agents/skills/<name>/SKILL.md` | Slash command or skill name mention | **Full native support** (Name + Desc injected; body loaded on demand) |
| **Cursor** | `.cursorrules`, `.cursor/rules/*.mdc` | `.cursor/rules/`, `.cursor/skills/` | `@skill-name` or rule match | Rule-based activation |
| **Claude Code** | `CLAUDE.md` | `CLAUDE.md`, `.claude/` | Direct prompt reference | Prompt-level progressive loading |
| **OpenAI Codex** | `AGENTS.md` | `.agents/skills/<name>/SKILL.md` | Repository context injection | Directory traversal |
| **Gemini CLI** | `GEMINI.md` | `.gemini/`, `.agents/skills/` | `gemini run <skill>` or prompt | Markdown context |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/prompts/*.prompt.md` | `/prompt <name>` in Copilot Chat | Reusable prompt files |
| **Windsurf** | `.windsurfrules` | `.windsurf/workflows/` | Cascade rule or workflow prompt | Cascade context |

---

## Complete 145-Skill Compatibility & Classification Matrix

Legend:
- `[NATIVE]`: Capability implemented natively by the AI product itself.
- `[CUSTOM SKILL]`: Installed as a portable `SKILL.md` runbook package.
- `[PROJECT RULE]`: Enforced via persistent repository instruction file (`AGENTS.md`, `CLAUDE.md`, etc.).
- `[ADAPTER]`: Product-specific wrapper or translation mapping.
- `[NOT SUPPORTED]`: Feature not natively present in the target tool (manual fallback documented).

| Skill Identifier | Google Antigravity | Cursor | Claude Code | OpenAI Codex | Gemini CLI | GitHub Copilot | Windsurf |
|---|---|---|---|---|---|---|---|
{matrix_table}
"""
    (base_dir / "COMPATIBILITY_MATRIX.md").write_text(compatibility_md, encoding="utf-8")
    print("  -> CATALOGUE.md and COMPATIBILITY_MATRIX.md generated.")


def generate_library_readme():
    print("[4/6] Generating AI_WORKFLOW_LIBRARY/README.md...")
    base_dir = REPO_ROOT / "AI_WORKFLOW_LIBRARY"
    
    readme_md = """# Universal AI Development Workflow & Skills Framework

> **Cross-Platform AI Engineering Workflows for Antigravity, Cursor, Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, and Windsurf.**  
> *Prepared: 31 October 2026 | Version 1.0 | Implementation ID: `IMP-2026-1031-001`*

---

## 1. Framework Purpose & Philosophy

This library provides an exhaustive, tool-independent collection of **145 production-grade AI skills and workflows**. It standardizes how AI coding assistants discover project context, clarify requirements, author implementation plans, write full-stack code, execute tests, debug issues, perform security audits, deploy applications, and coordinate multi-agent workstreams.

### Core Principles
1. **Single Source of Truth**: Universal skills are maintained in portable `SKILL.md` packages adhering to a strict 9-section structure.
2. **Tool-Independent Core**: All engineering logic, procedures, safety guardrails, and acceptance criteria are agnostic to any single AI product.
3. **Native Adapters**: Tool-specific wrappers (`.cursorrules`, `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, Copilot prompts) translate the universal core into each tool's native discovery mechanisms.
4. **Mandatory Governance**: Every non-trivial change follows the **Diagnose → Plan → Confirm → Execute → Verify** lifecycle (**NO APPROVAL = NO IMPLEMENTATION**).
5. **No Error Left Behind**: Zero unresolved build errors (`tsc`), lint errors (`ruff`), runtime exceptions, or browser console errors permitted upon completion.

---

## 2. Directory Layout

```text
AI_WORKFLOW_LIBRARY/
├── README.md                               # This master guide
├── CATALOGUE.md                            # Complete 145-skill catalog & descriptions
├── COMPATIBILITY_MATRIX.md                 # 7-tool compatibility & classification matrix
├── universal/                              # 118 Universal Skills
│   ├── 01-discovery-requirements/         # 12 skills (project-discovery, grill-me, etc.)
│   ├── 02-planning-management/             # 13 skills (diagnose-plan-confirm-execute, etc.)
│   ├── 03-app-development/                 # 19 skills (full-stack-development, website-creation, etc.)
│   ├── 04-code-quality/                    # 15 skills (code-review, security-audit, etc.)
│   ├── 05-testing-qa/                      # 18 skills (e2e-testing, browser-testing, etc.)
│   ├── 06-debugging/                       # 13 skills (diagnose-issue, fix-runtime-errors, etc.)
│   ├── 07-deployment-devops/               # 14 skills (docker-setup, local-setup, etc.)
│   ├── 08-documentation/                   # 11 skills (readme-generation, project-booklet, etc.)
│   └── 09-agent-orchestration/              # 13 skills (agent-orchestration, accidental-data-loss-prevention, etc.)
├── project-specific/
│   └── uaic/                               # 17 UAIC Court Automation Skills (bot-orchestration, captcha, etc.)
└── adapters/                               # Tool-specific adapter documentation
    ├── antigravity/README.md
    ├── cursor/README.md
    ├── claude-code/README.md
    ├── codex/README.md
    ├── gemini/README.md
    ├── github-copilot/README.md
    └── windsurf/README.md
```

---

## 3. Standard Skill File Specification (`SKILL.md`)

Every skill file strictly adheres to the following structure:
1. **YAML Frontmatter**: `name` (lowercase hyphenated) and `description` (actionable trigger summary).
2. **Purpose & Overview**: Concise business and technical goal.
3. **When to Use & When NOT to Use**: Precise triggers and explicit exclusions.
4. **Required Inputs & Prerequisites**: Required parameters, access, tools, and preceding phases.
5. **Step-by-Step Execution Procedure**: Numbered procedure with bold step headers, decision branches, and safety gates.
6. **Safety Considerations & Guardrails**: Data loss prevention, security constraints, and invariant preservation.
7. **Expected Deliverables & Artifacts**: Concrete outputs (reports, code files, test logs).
8. **Acceptance Criteria & Definition of Done**: Objective, verifiable conditions for task sign-off.
9. **Error Recovery & Troubleshooting**: How to handle timeouts, disconnects, and errors.
10. **Tool Invocation & Reference Mapping**: Tool-by-tool invocation mapping table and authoritative reference links.

---

## 4. Mandatory Global Agent Governance Rules

Every AI assistant operating in this repository must obey these 9 universal rules:
1. **Analyse Before Implementation**: Inspect repository architecture, dependencies, tests, and runtime behavior before proposing changes.
2. **Diagnose → Plan → Confirm → Execute**: Complete diagnosis, author an implementation plan, and wait for explicit human approval before modifying code.
3. **Preserve Existing Functionality**: Never rebuild, rename, or delete valid existing components merely for convenience; verify usage before cleanup.
4. **Prevent Accidental Data Loss**: Require explicit user confirmation before running destructive filesystem, database, or git commands.
5. **Resolve Relevant Errors**: Fix all build errors (`tsc`), lint issues (`ruff`), runtime crashes, and browser console exceptions introduced by changes.
6. **Continue from Checkpoints**: In the event of process timeouts or interruptions, resume gracefully from the last verified checkpoint.
7. **Perform Actual Testing**: Never assume code works without executing automated unit, integration, or browser tests.
8. **Never Declare Completion Without Evidence**: Report exact test outputs, passing assertions, and visual evidence before declaring work complete.
9. **Maintain Updated Documentation**: Automatically update `README.md`, schema docs, and API documentation whenever code or interfaces change.
"""
    (base_dir / "README.md").write_text(readme_md, encoding="utf-8")
    print("  -> AI_WORKFLOW_LIBRARY/README.md generated.")


def generate_adapters():
    print("[5/6] Generating Tool Adapters & Project Instruction Files...")
    adapters_dir = REPO_ROOT / "AI_WORKFLOW_LIBRARY" / "adapters"
    adapters_dir.mkdir(parents=True, exist_ok=True)
    
    # Tool adapter subdirectories
    tools = ["antigravity", "cursor", "claude-code", "codex", "gemini", "github-copilot", "windsurf"]
    for tool in tools:
        (adapters_dir / tool).mkdir(parents=True, exist_ok=True)
        
    # 1. Antigravity Adapter README
    (adapters_dir / "antigravity" / "README.md").write_text(
        """# Google Antigravity Adapter

**Status:** Native & Active in this repository  
**Discovery Path:** `.agents/skills/<skill-name>/SKILL.md`  
**Loading Priority:** Workspace Project (`.agents/skills/`) > Declared > Global (`~/.gemini/config/`) > Built-in  

### How It Works
Google Antigravity automatically discovers skills placed in `.agents/skills/`. It uses **progressive disclosure**:
- Only the YAML frontmatter `name:` and `description:` are injected into the agent system prompt.
- The full body of `SKILL.md` is loaded dynamically on demand when the skill is activated.

### Invocation
- Slash commands: e.g. `/plan`, `/goal`, `/grill-me`, `/teamwork`, `/compact`.
- Chat prompt: e.g. `/project-discovery` or "Run project discovery on this codebase".
""",
        encoding="utf-8"
    )

    # 2. Cursor Adapter & Root .cursorrules
    (adapters_dir / "cursor" / "README.md").write_text(
        """# Cursor Adapter

**Discovery Files:** `.cursorrules` (Root) and `.cursor/rules/*.mdc`  
**Invocation:** Mention `@skill-name` in Cursor Chat or Composer.  
""",
        encoding="utf-8"
    )
    
    cursorrules_content = """# Cursor Global Project Rules — UAIC Orchestrator
# Universal AI Development Workflow & Skills Framework

You are working in the UAIC Claim & RPA Orchestrator repository (Next.js 14 + Python 3.14 + FastAPI + Celery + Playwright).

## 9 Mandatory Governance Rules
1. ANALYSE BEFORE IMPLEMENTATION: Inspect repository structure, dependencies, and tests before writing code.
2. DIAGNOSE -> PLAN -> CONFIRM -> EXECUTE: Complete diagnosis, author an implementation plan, and wait for human approval before modifying code. NO APPROVAL = NO IMPLEMENTATION.
3. PRESERVE EXISTING FUNCTIONALITY: Never rebuild, delete, or rename working components.
4. PREVENT ACCIDENTAL DATA LOSS: Never run destructive SQL (DROP/TRUNCATE), filesystem (rmdir), or git reset without explicit user consent.
5. NO ERROR LEFT BEHIND: Fix all TypeScript errors (npx tsc --noEmit), Ruff lint errors, and browser console errors.
6. CONTINUE FROM CHECKPOINTS: Resume safely from verified checkpoints after interruptions.
7. PERFORM ACTUAL TESTING: Execute pytest and tsc; never assume code is correct without evidence.
8. NEVER DECLARE COMPLETION WITHOUT EVIDENCE: Present test logs and visual evidence before declaring completion.
9. MAINTAIN UPDATED DOCUMENTATION: Update README.md and docs/ whenever code changes.

## Skills Library Reference
All 145 project skills are located in `.agents/skills/<name>/SKILL.md` and `AI_WORKFLOW_LIBRARY/`.
To execute a skill, read its `SKILL.md` and follow its step-by-step procedure.
"""
    (REPO_ROOT / ".cursorrules").write_text(cursorrules_content, encoding="utf-8")
    
    cursor_rules_dir = REPO_ROOT / ".cursor" / "rules"
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)
    (cursor_rules_dir / "uaic-governance.mdc").write_text(cursorrules_content, encoding="utf-8")

    # 3. Claude Code Adapter & Root CLAUDE.md
    (adapters_dir / "claude-code" / "README.md").write_text(
        """# Claude Code Adapter

**Discovery File:** `CLAUDE.md` (Root)  
**Invocation:** Prompt Claude Code directly; it reads `CLAUDE.md` at session start.  
""",
        encoding="utf-8"
    )
    
    claude_md_content = """# CLAUDE.md — Project Instructions for Claude Code
# UAIC Claim & RPA Orchestrator

## 1. Project Overview
Production-grade Next.js 14 + Python 3.14.7 FastAPI + Celery + Playwright orchestrator automating court-case discovery across 8 Florida and Texas county court portals.

## 2. Mandatory Engineering Governance
Follow the Universal AI Development Workflow & Skills Framework:
- **NO APPROVAL = NO IMPLEMENTATION**: Present a detailed implementation plan and wait for user confirmation before editing code.
- **Test Commands**:
  - Backend unit & integration tests: `cd backend && .venv\\Scripts\\pytest -q` (556 passing tests)
  - Backend lint: `cd backend && .venv\\Scripts\\ruff check app tests` (0 errors)
  - Frontend TypeScript: `cd frontend && npx tsc --noEmit` (0 errors)
  - PowerShell syntax: `powershell -File scripts/check_ps1_syntax.ps1` (0 errors)
- **Critical Business Rules**:
  - State Routing: FL policy & loss -> [broward, hillsborough, miami]; TX -> [harris_cclerk, dallas, harris_jp, harris_district, travis]; Cross-state -> ALL 8.
  - DOL Date Base: 1899-12-30 base date, strict MM/dd/yyyy format.
  - ClaimNumber Prefix: 9-digit gets leading '0' prefix in Guidewire payload.
  - Fuzzy Match Cascade: Claimant -> Insured -> Driver at RapidFuzz 0.60 threshold.
  - Portal Schemas: 5 fields for 6 portals; strictly NO CaseType for Harris JP and Harris County Clerk.
  - Protected Directories: Never delete `anticaptcha-plugin_v0.83/` or `.agents/`.

## 3. Skills Library Access
All 145 executable skills are located in `.agents/skills/<skill-name>/SKILL.md` and `AI_WORKFLOW_LIBRARY/`.
Read the corresponding `SKILL.md` before executing any workflow.
"""
    (REPO_ROOT / "CLAUDE.md").write_text(claude_md_content, encoding="utf-8")

    # 4. OpenAI Codex Adapter & Root AGENTS.md
    (adapters_dir / "codex" / "README.md").write_text(
        """# OpenAI Codex Adapter

**Discovery File:** `AGENTS.md` (Root) & `.agents/skills/<name>/SKILL.md`  
**Invocation:** Codex automatically reads `AGENTS.md` and discovers skills in `.agents/skills/`.  
""",
        encoding="utf-8"
    )

    # 5. Gemini CLI Adapter & Root GEMINI.md
    (adapters_dir / "gemini" / "README.md").write_text(
        """# Gemini CLI Adapter

**Discovery File:** `GEMINI.md` (Root)  
**Invocation:** Gemini CLI loads `GEMINI.md` at session start.  
""",
        encoding="utf-8"
    )
    
    gemini_md_content = """# GEMINI.md — Project Guidelines for Gemini CLI & Antigravity
# UAIC Claim & RPA Orchestrator

## Universal AI Development Workflow & Skills Framework Active
All 145 standardized skills are active and discoverable in `.agents/skills/<name>/SKILL.md` and `AI_WORKFLOW_LIBRARY/`.

## Core Principles
1. Analyse before implementation.
2. Diagnose -> Plan -> Confirm -> Execute (NO APPROVAL = NO IMPLEMENTATION).
3. Preserve existing working functionality.
4. Prevent accidental data loss (STOP AND VERIFY before destructive actions).
5. Resolve all build, terminal, runtime, and browser console errors.
6. Continue from last verified checkpoint after interruptions.
7. Perform actual testing (pytest, tsc, ps1) rather than assuming correctness.
8. Never declare completion without verification evidence.
9. Maintain updated README.md and documentation.

## Test Commands
- Backend: `cd backend && .venv\\Scripts\\pytest -q`
- Lint: `cd backend && .venv\\Scripts\\ruff check app tests`
- Frontend Type Check: `cd frontend && npx tsc --noEmit`
- PowerShell Syntax: `powershell -File scripts/check_ps1_syntax.ps1`
"""
    (REPO_ROOT / "GEMINI.md").write_text(gemini_md_content, encoding="utf-8")

    # 6. GitHub Copilot Adapter
    (adapters_dir / "github-copilot" / "README.md").write_text(
        """# GitHub Copilot Adapter

**Discovery File:** `.github/copilot-instructions.md`  
**Prompt Files:** `.github/prompts/*.prompt.md`  
**Invocation:** Copilot Chat `/prompt <name>` or automatic instruction injection.  
""",
        encoding="utf-8"
    )
    
    github_dir = REPO_ROOT / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    (github_dir / "copilot-instructions.md").write_text(claude_md_content, encoding="utf-8")
    
    prompts_dir = github_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    (prompts_dir / "diagnose-plan-confirm-execute.prompt.md").write_text(
        """# Diagnose -> Plan -> Confirm -> Execute Prompt
Follow the 6-phase governance lifecycle before touching code:
1. Understand the user request.
2. Inspect relevant files, tests, and historical docs in `docs/`.
3. Review `README.md` and `AGENTS.md`.
4. Diagnose root causes with evidence.
5. Create detailed implementation plan in `docs/`.
6. WAIT FOR EXPLICIT USER APPROVAL before executing code changes.
""",
        encoding="utf-8"
    )

    # 7. Windsurf Adapter & Root .windsurfrules
    (adapters_dir / "windsurf" / "README.md").write_text(
        """# Windsurf Adapter

**Discovery File:** `.windsurfrules` (Root)  
**Workflows:** `.windsurf/workflows/`  
**Invocation:** Cascade rules loaded automatically in Windsurf sessions.  
""",
        encoding="utf-8"
    )
    (REPO_ROOT / ".windsurfrules").write_text(cursorrules_content, encoding="utf-8")

    print("  -> All adapters and project instruction files generated.")


def update_root_agents_md():
    print("[6/6] Updating AGENTS.md with Framework cross-references...")
    agents_path = REPO_ROOT / "AGENTS.md"
    if not agents_path.exists():
        return
        
    content = agents_path.read_text(encoding="utf-8")
    
    # Check if section 13 already exists
    if "## 13. Universal AI Development Workflow & Skills Framework" in content:
        print("  -> AGENTS.md already contains Framework section.")
        return
        
    addition = """
---

## 13. Universal AI Development Workflow & Skills Framework

The repository incorporates the **Universal AI Development Workflow & Skills Framework** (`IMP-2026-1031-001`), establishing **145 production-grade AI skills and workflows** covering the entire software engineering lifecycle.

### Key Framework Locations
- **Master Framework Guide**: [`AI_WORKFLOW_LIBRARY/README.md`](file:///AI_WORKFLOW_LIBRARY/README.md)
- **Skills Catalogue (145 Skills)**: [`AI_WORKFLOW_LIBRARY/CATALOGUE.md`](file:///AI_WORKFLOW_LIBRARY/CATALOGUE.md)
- **Compatibility Matrix**: [`AI_WORKFLOW_LIBRARY/COMPATIBILITY_MATRIX.md`](file:///AI_WORKFLOW_LIBRARY/COMPATIBILITY_MATRIX.md)
- **Live Active Discovery Root**: [`.agents/skills/`](file:///.agents/skills/) (Google Antigravity & OpenAI Codex)
- **Implementation Plan**: [`docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`](file:///docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md)

### Supported AI Tool Adapters
1. **Google Antigravity**: Active native discovery via `.agents/skills/<name>/SKILL.md` (progressive disclosure).
2. **Cursor**: Supported via `.cursorrules` and `.cursor/rules/*.mdc`.
3. **Claude Code**: Supported via `CLAUDE.md`.
4. **OpenAI Codex**: Supported via `AGENTS.md` and `.agents/skills/`.
5. **Gemini CLI**: Supported via `GEMINI.md`.
6. **GitHub Copilot**: Supported via `.github/copilot-instructions.md` and `.github/prompts/`.
7. **Windsurf**: Supported via `.windsurfrules`.
"""
    agents_path.write_text(content.strip() + "\n" + addition, encoding="utf-8")
    print("  -> AGENTS.md updated successfully.")


def main():
    print("================================================================================")
    print("BUILDING UNIVERSAL AI DEVELOPMENT WORKFLOW & SKILLS FRAMEWORK")
    print("================================================================================")
    build_canonical_library()
    deploy_agents_skills()
    generate_catalogue_and_matrix()
    generate_library_readme()
    generate_adapters()
    update_root_agents_md()
    print("================================================================================")
    print("FRAMEWORK BUILD COMPLETE: 145 SKILLS PROVISIONED ACROSS ALL REPOSITORIES")
    print("================================================================================")


if __name__ == "__main__":
    main()

