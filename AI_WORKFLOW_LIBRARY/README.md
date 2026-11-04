# Universal AI Development Workflow & Skills Framework

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
