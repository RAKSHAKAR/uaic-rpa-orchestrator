---
name: project-task-router
description: >
  Autonomous task dispatcher for the UAIC Claim & RPA Orchestrator.
  Classifies user requests into 27 task categories, automatically selects
  the appropriate skill chain from the project skill registry, checks
  prerequisites and approval thresholds, and executes the selected workflow.
  This is the primary entry point of the UAIC AI Engineering Operating System.
version: 1.0.0
implementation_id: IMP-2026-1103-002
last_updated: 2026-11-03
---

# Project Task Router Skill

## Purpose

Provide zero-manual-workflow-selection capability for the UAIC project. The user
states a task in plain English; this skill classifies it, selects the right
skills, and executes the work using the correct Antigravity workflows.

## Scope

All engineering tasks for the UAIC Claim & RPA Orchestrator:
- Backend (Python/FastAPI/Celery)
- Frontend (Next.js/TypeScript/React)
- Browser automation (Playwright/Chrome/CAPTCHA)
- Database (SQLite/SQLAlchemy)
- Integrations (Guidewire, SMTP, AntiCaptcha)
- Testing, documentation, deployment

**Out of scope:** GCP data pipelines, scientific research, mobile native apps.

## Trigger Conditions

Activate at the beginning of EVERY user task in this repository. This skill
is always the first step — it determines what happens next.

## Prerequisites

Before routing:
1. Read `.agent/PROJECT_CONTEXT.md` (fast bootstrap if not already loaded)
2. Read `.agent/PROJECT_RULES.md` (enforcement rules)
3. Confirm working directory is `d:\scratch\Bot_UAIC`

## Workflow Steps

### Step 1 — Parse User Intent

Read the user request carefully. Identify:
- **Action type**: Fix, Build, Add, Analyze, Test, Document, Deploy, Optimize, Review
- **Target component**: Frontend, Backend, Database, Scraper, Queue, Integration, Documentation
- **Urgency**: Normal, Urgent (production incident), Emergency
- **Data risk**: Does this touch production data, the database, or external systems?

### Step 2 — Classify Task

Map to one of 27 categories from `.agent/TASK_ROUTING_MATRIX.md`:

1. Requirements analysis
2. Architecture review
3. Gap analysis
4. Backend bug fix
5. Frontend bug fix
6. API bug fix
7. Database bug fix
8. Browser automation bug fix
9. New API endpoint
10. New frontend route/page
11. New React component
12. UI/UX redesign
13. Design system update
14. Database schema change
15. New database model
16. Third-party API integration
17. Guidewire integration change
18. Scraper change
19. CAPTCHA handling change
20. Fuzzy matching change
21. Queue/Celery change
22. Notification system change
23. Settings system change
24. Export/import change
25. Security fix/audit
26. Performance optimization
27. Accessibility fix

A task may span multiple categories. Use the most specific primary category
and invoke supporting categories as secondary skills.

### Step 3 — Safety Gate

Check before proceeding:

```
If task involves:
  - Production data deletion → STOP → invoke accidental-data-loss-prevention
  - Database schema change → Require explicit backup confirmation
  - Exposed credentials → IMMEDIATE STOP → invoke security-audit
  - Production deployment → Require explicit authorization
  - External API with real credentials → Confirm sandbox vs. production
```

### Step 4 — Look Up Skill Chain

Open `.agent/PROJECT_SKILL_REGISTRY.md`.

Find the row matching the task category. Note:
- **Primary Skill** — read its SKILL.md completely before executing
- **Supporting Skills** — invoke as directed by the primary skill
- **Approval Required** — if YES, prepare and present plan BEFORE implementing

### Step 5 — Check Approval Threshold

```
Approval NOT required for:
  - Documentation-only changes
  - New test files
  - Reading/analysis tasks
  - Skill creation/repair

Approval REQUIRED for:
  - Any source code modification
  - Any database change
  - Any configuration change
  - Any file deletion/move

Present a plan to the user and wait for explicit approval before implementing.
```

### Step 6 — Read Primary Skill Instructions

Open `.agents/skills/<primary-skill>/SKILL.md` and read it completely.
Follow its exact workflow — do not skip steps.

### Step 7 — Execute Workflow

Follow the primary skill's steps. Invoke supporting skills at the points
they are directed. Maintain the Understand → Plan → Confirm → Implement →
Test → Verify → Document sequence.

### Step 8 — Apply Quality Gate

After implementation, run the full mandatory quality gate:

```powershell
# If Python changed:
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m ruff check app tests
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests --tb=short -q

# If TypeScript changed:
Set-Location d:\scratch\Bot_UAIC\frontend; npx tsc --noEmit
Set-Location d:\scratch\Bot_UAIC\frontend; npm run lint

# If .ps1 changed:
powershell -NoProfile -ExecutionPolicy Bypass -File "d:\scratch\Bot_UAIC\scripts\check_ps1_syntax.ps1"

# If docker-compose.yml changed:
docker compose -f d:\scratch\Bot_UAIC\docker-compose.yml config
```

All checks must pass with zero errors. Fix any failures before declaring done.

### Step 9 — Update CHANGELOG

Open `.agent/CHANGELOG.md` and add a new entry:

```markdown
## [IMP-YYYY-MMDD-NNN] — YYYY-MM-DD — <Short Task Name>

### What Changed
- <File 1>: <what and why>
- <File 2>: <what and why>

### Source Code Modified
<List or "None">

### Test Results
<Actual output from quality gate>
```

### Step 10 — Deliver Report

Provide to the user:
- What was done
- Files modified (with links)
- Test results (actual output, not fabricated)
- Remaining issues or limitations
- Recommended next steps

## Applicable Tools

- `run_command` — execute quality gate commands
- `write_file` / `edit_file` — implement changes
- `read_file` — inspect existing code
- `search_marketplace` — if a plugin would help
- `invoke_subagent` — for parallelizable sub-tasks

## Approval Requirements

- Required for all source code changes
- Present plan as artifact with RequestFeedback=true
- Wait for explicit user approval before executing implementation

## Safety Restrictions

- NEVER implement before plan approval
- NEVER fabricate test results
- NEVER delete tests to make the suite pass
- NEVER touch `.agents/skills/` without explicit request
- NEVER touch `anticaptcha-plugin_v0.83/` directory
- NEVER bypass the quality gate

## Validation Criteria

Task is complete when:
1. All quality gate checks pass (0 errors)
2. No stale "in progress" status left in documentation
3. `.agent/CHANGELOG.md` is updated
4. User has received delivery report with actual test evidence

## Error Handling

| Error | Action |
|---|---|
| Task category ambiguous | Use `grill-me` skill to clarify with targeted questions |
| Required skill missing from `.agents/skills/` | Check `AI_WORKFLOW_LIBRARY/CATALOGUE.md`; create skill only if not available |
| Quality gate fails | Fix root cause; do NOT suppress errors or disable checks |
| Approval not given | Stop; do not implement; ask for clarification |
| Production data at risk | Invoke `accidental-data-loss-prevention` immediately |

## Examples of Appropriate Usage

### Example 1 — Bug Fix
```
User: "The claims dashboard is showing wrong counts in the stat cards"
→ Classify: Category 5 (Frontend bug fix)
→ Skills: diagnose-plan-confirm-execute → fix-ui-issues → fix-console-errors
→ Approval: YES (code change)
→ Execute: Inspect → diagnose → plan → implement → test (tsc + lint) → verify
```

### Example 2 — New Feature
```
User: "Add a notifications page to the frontend"
→ Classify: Category 10 (New frontend route/page)
→ Skills: frontend-development → component-development → theme-system → responsive-ui-development
→ Approval: YES (new code)
→ Execute: Check backend endpoint exists → design component → implement → tsc → lint → browser verify
```

### Example 3 — Documentation
```
User: "Update the README with the new endpoint"
→ Classify: Category 32 (README update)
→ Skills: readme-generation → documentation-sync
→ Approval: NO
→ Execute: Read README → update endpoint table → update changelog → done
```

### Example 4 — Testing
```
User: "Run the full test suite and show me the results"
→ Classify: Run tests (no skill needed — direct command execution)
→ Approval: NO
→ Execute: Run pytest → capture output → report actual results
```

