---
name: project-repository-intelligence
description: >
  Fast repository context loader for new AI sessions on the UAIC project.
  Reads project context files to establish full architectural understanding
  in under 60 seconds, without requiring re-reading the entire codebase.
  Reports project state, recent changes, and session readiness.
version: 1.0.0
implementation_id: IMP-2026-1103-002
last_updated: 2026-11-03
---

# Project Repository Intelligence Skill

## Purpose

Bootstrap a new AI session for the UAIC project with complete architectural
context in the minimum number of file reads. Avoids the time cost of
re-discovering everything from scratch each session.

## Scope

Context loading for the UAIC Claim & RPA Orchestrator only.

## Trigger Conditions

Activate as the FIRST action in any new conversation about the UAIC project,
before reading any source code files.

## Prerequisites

- Working directory: `d:\scratch\Bot_UAIC`
- `.agent/` directory exists (created by IMP-2026-1103-002)

## Workflow Steps

### Step 1 — Read AI OS Context Files (in order)

```
Priority 1: .agent/PROJECT_CONTEXT.md          (project overview, rules, commands)
Priority 2: .agent/CHANGELOG.md                (last known changes)
Priority 3: .agent/PROJECT_RULES.md            (enforcement rules)
Priority 4: .agent/PROJECT_SKILL_REGISTRY.md   (skill routing — load if task is ready)
```

Read Priority 1 and 2 always. Read 3 and 4 only if proceeding to a task.

### Step 2 — Spot-Check Critical Files (5 checks)

Confirm these files exist and haven't been removed:

```
1. backend/app/main.py                          (FastAPI entry point)
2. backend/app/automation/base.py               (BaseCourtScraper)
3. backend/app/services/fuzzy_engine.py         (RapidFuzz cascade)
4. frontend/src/app/layout.tsx                  (Next.js root layout)
5. backend/orchestrator.db                      (Active database)
```

If any are missing: alert the user immediately — do not proceed.

### Step 3 — Check Recent Changes

Read `.agent/CHANGELOG.md` — note the most recent implementation ID and what changed.

If the changelog shows very recent changes, also check:
- Were all quality gates confirmed as passed?
- Are there any "in progress" or "pending" statuses left?

### Step 4 — Validate Skill Registry (if task is being routed)

If the user has a task ready, open `.agent/PROJECT_SKILL_REGISTRY.md` and
identify the applicable row before doing anything else.

### Step 5 — Report Session Readiness

Respond with a brief status message:

```
✅ UAIC session loaded.
- Project: UAIC Claim & RPA Orchestrator (v1.0.0 RC, production-deployed)
- Last change: [IMP-ID from CHANGELOG] on [date] — [brief description]
- Critical files: 5/5 present
- Skill registry: 44 task categories mapped
- Ready for tasks. What would you like to work on?
```

If anything is wrong or missing, report the specific issue before proceeding.

## Applicable Tools

- `read_file` — read context files
- `run_command` — spot-check file existence

## Approval Requirements

None — this is a read-only context loading operation.

## Safety Restrictions

- Do NOT modify any files during context loading
- Do NOT run tests during context loading (unless requested)
- Do NOT read source code files unless context files are stale or missing

## Validation Criteria

Session is bootstrapped when:
1. `.agent/PROJECT_CONTEXT.md` has been read and processed
2. `.agent/CHANGELOG.md` has been read
3. 5 spot-check files confirmed present
4. Session readiness reported to user

## Error Handling

| Error | Action |
|---|---|
| `.agent/` directory missing | Fall back to reading `AGENTS.md` and `README.md` directly |
| `PROJECT_CONTEXT.md` missing | Read `AGENTS.md` §1-5 + `README.md` as fallback |
| Spot-check file missing | Alert user; do NOT proceed with task until investigated |
| CHANGELOG shows uncommitted "in progress" work | Report to user; ask if they want to resume or start fresh |

## Output Format

```markdown
✅ **UAIC session ready**
- **Platform:** UAIC Claim & RPA Orchestrator
- **Status:** v1.0.0 RC — Production-deployed
- **Last change:** IMP-YYYY-MMDD-NNN (YYYY-MM-DD) — [description]
- **Critical files:** 5/5 confirmed
- **AI OS:** Active (44 skill routes mapped)

Ready for your next task. What would you like to work on?
```

