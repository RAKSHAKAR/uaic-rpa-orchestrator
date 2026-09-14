---
name: diagnose-plan-confirm-execute
description: |
  Universal AI Engineering Governance Skill.
  Enforces the complete lifecycle: Understand → Inspect → Review README → Review History →
  Diagnose → Gap Analysis → Plan → Save to implementation_plan → Show User → Wait for Approval →
  Implement → Test → Validate → Document → Human Verify → Archive.
  CRITICAL: NO APPROVAL = NO IMPLEMENTATION. AI-generated documentation stays in
  implementation_plan/ until the HUMAN explicitly verifies it.
  Applies to ALL engineering activities: features, bugs, refactoring, architecture,
  database, APIs, UI/UX, auth, DevOps, integrations, automation, performance, security,
  testing, troubleshooting, documentation, migration, maintenance.
---

# Universal AI Engineering Governance Skill

## THE ABSOLUTE GOVERNANCE RULE

> **AI MUST NOT RUSH FROM REQUEST → CODE.**
>
> **NO APPROVAL = NO IMPLEMENTATION.**
>
> **AI-GENERATED DOCUMENTATION STAYS IN `implementation_plan/` UNTIL THE HUMAN EXPLICITLY VERIFIES IT.**

---

## Required Lifecycle (Mandatory — Non-Negotiable)

```text
┌──────────────────────────────┐
│         USER REQUEST         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│          UNDERSTAND          │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     INSPECT CODE / CONFIG    │
│   Architecture / Tests /     │
│   Routes / DB / APIs / Env   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│   REVIEW README.md           │
│  Preserve + Understand All   │
│     Existing Information     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│  REVIEW implementation_plan/ │
│  AND implementation_plan/ HISTORY     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│          DIAGNOSE            │
│  Root Cause + Evidence Only  │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        GAP ANALYSIS          │
│  Current vs Expected State   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│   DETAILED IMPLEMENTATION    │
│         PLAN                 │
│ Requirements + Scope +       │
│ Files + Tests + Risks +      │
│ Acceptance Evidence          │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ SAVE PLAN TO                 │
│ implementation_plan/         │
│       implementation_plan/            │
│  Status: Awaiting Approval   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     SHOW PLAN TO USER        │
└──────────────┬───────────────┘
               ↓
       ┌───────────────┐
       │  WAIT FOR     │
       │ EXPLICIT USER │
       │   APPROVAL    │
       └───────┬───────┘
               │
       NO ─────┴───── YES
       ↓               ↓
     STOP          RECORD APPROVAL
                       ↓
                   IMPLEMENT
                       ↓
                 UPDATE README.md
                       ↓
              UPDATE IMPLEMENTATION
                  DOCUMENTATION
                       ↓
                  RUN TESTS
                       ↓
                   VALIDATE
                       ↓
              REGRESSION CHECK
                       ↓
            DOCUMENT ACTUAL RESULT
                       ↓
           DOCUMENT DEVIATIONS
                       ↓
           FINAL DOCUMENTATION →
          implementation_plan/
               implementation_plan/
                       ↓
         ASK USER TO VERIFY DOCS
                       ↓
               ┌───────┴───────┐
               │               │
          NOT VERIFIED      VERIFIED
               │               │
               ↓               ↓
           KEEP IN         MOVE TO
          implementation_plan       PERMANENT
                            HISTORY
```

---

## Stage 1 — Understand the Request

Before touching any file, deeply analyze the user's prompt:

1. **Requested Objective**: What exact outcome is the user asking for?
2. **Problem Statement**: What is broken, missing, or suboptimal?
3. **Expected Behavior**: What should happen once complete?
4. **Actual Behavior**: What currently happens?
5. **Scope**: Which modules, layers, or services are affected?
6. **Constraints**: Stack, versions, patterns, backward compatibility, security.
7. **Acceptance Criteria**: Translate into measurable, testable checklist items.

> **Ambiguity Rule**: If requirements are underspecified, formulate clarifying questions. DO NOT invent requirements silently.

---

## Stage 2 — Inspect the Existing System

Never assume something is missing. Always inspect the actual codebase:

- **Repository Structure**: Directories, configs, build scripts.
- **Frontend**: Routes, components, state, API clients, themes, responsiveness.
- **Backend**: Endpoints, services, Celery workers, middleware, schemas.
- **Database**: ORM models, migrations, relationships, indexes, constraints.
- **Testing**: Pytest, Jest, mock fixtures, test coverage.
- **Infrastructure**: Dockerfiles, docker-compose.yml, env vars, health checks.
- **README.md**: The living technical booklet — read it fully.
- **`implementation_plan/`**: All historical plans, walkthroughs, gap analyses.
- **`implementation_plan/`**: Unverified AI working documents.

### Search Strategy
```
REUSE → EXTEND → REFACTOR → CREATE NEW
```
Always check if existing code already fulfills part of the requirement.

---

## Stage 3 — Review Implementation History

Before creating any new plan, inspect:

```
implementation_plan/
implementation_plan/
```

Identify:
- What has already been done?
- What was planned but not implemented?
- What previously failed?
- What decisions were made and why?
- Does the current request duplicate or conflict with existing work?
- Are there unresolved gaps or known limitations?

> **Historical documentation is evidence, not absolute truth. Always compare against actual current implementation.**

---

## Stage 4 — Diagnose

For bugs, regressions, or integration issues, confirm root cause with evidence:

```text
Problem:           [Clear failure summary]
Expected Behavior: [Per specification]
Actual Behavior:   [What happens, with error logs/traces]
Evidence:          [Exact log lines / code lines / test output]
Root Cause:        [Underlying mechanism — not just the symptom]
Contributing:      [Secondary factors: env, race conditions, type mismatches]
Affected Areas:    [All impacted files, endpoints, data models]
Solution:          [High-level approach to fix the root cause]
```

> **Grounding Rule**: If root cause cannot be proven, state: *"Root cause not yet confirmed. Additional investigation required."* Never guess.

---

## Stage 5 — Gap Analysis

Document:
- Current state
- Expected state
- Missing functionality
- Partially implemented functionality
- Broken functionality
- Architectural gaps
- Security gaps
- Testing gaps

```text
Gap:    [Description]
Impact: [Business/technical risk]
Action: [Included in this plan | Recorded as follow-up]
```

If a discovered gap is unrelated to the approved task, **DO NOT silently fix it**. Document it as a follow-up item.

---

## Stage 6 — Detailed Implementation Plan

The plan must be detailed enough for any senior engineer to execute without ambiguity.

Required sections:

- **Problem / Request**
- **Current State**
- **Root Cause**
- **Gap Analysis**
- **Requirements**
- **Scope** (what IS included)
- **Out of Scope** (what will NOT change)
- **Files / Modules** expected to change
- **Architecture** — how the change fits
- **Database** — schema/data changes required
- **API** — endpoint changes
- **Frontend** — UI/UX changes
- **Backend** — service/logic changes
- **Configuration** — env/config changes
- **Security** — considerations
- **Testing** — tests to add/run
- **Regression** — existing behavior to preserve
- **Acceptance Criteria** — measurable, observable evidence
- **Risks** — what can go wrong
- **Rollback** — how to reverse

### File-Level Action Plan
```markdown
#### [MODIFY] `backend/app/services/example.py`
- Change: [Specific change]
- Reason: [Why this change is necessary]

#### [NEW] `frontend/src/components/Example.tsx`
- Change: [What will be created]
- Reason: [Why it's needed]

#### [DELETE] `backend/legacy_module.py`
- Change: [What is removed]
- Reason: [Why it's safe to remove]
```

---

## Stage 7 — Save Plan to `implementation_plan/`

**Before showing the plan to the user, save it.**

### Naming Convention
```
YYYY-MM-DD_<project-or-module>_<feature-or-task>_<document-type>_v<version>.md
```

Examples:
```
2026-09-05_uaic_directory-restructure_implementation-plan_v1.md
2026-09-05_uaic_directory-restructure_gap-analysis_v1.md
2026-09-05_uaic_directory-restructure_walkthrough_v1.md
2026-09-05_uaic_directory-restructure_test-report_v1.md
2026-09-05_uaic_directory-restructure_validation_v1.md
```

Avoid: `plan.md`, `notes.md`, `final.md`, `temp.md`, `updated.md`

### Implementation ID
Every substantial implementation must have a unique ID:
```
IMP-YYYY-MMDD-NNN
Example: IMP-2026-0905-001
```

### Required Document Metadata
```markdown
# Implementation Record

Implementation ID:   IMP-YYYY-MMDD-NNN
Project:             [Project name]
Module:              [Module]
Feature / Issue:     [Feature or task]
Document Type:       Implementation Plan | Gap Analysis | Walkthrough | Change Log | Test Report | Validation
Version:             v1
Status:              Awaiting Approval | Complete
Created:             YYYY-MM-DD
Last Updated:        YYYY-MM-DD
AI Agent:            Antigravity / Claude / Gemini / etc.
Approval Status:     Pending | Approved
Approved By:         Pending | User
Approval Date:       Pending | YYYY-MM-DD
AI Verification:     Complete (100% Automated Testing Suite)
```

### The Plan Saved ≡ The Plan Shown

> The plan saved in `implementation_plan/` MUST be the same substantive plan shown to the user. Never present one plan while secretly saving another.

---

## Stage 8 — Show Plan and Wait for Explicit Approval

Present the plan. Then **STOP**.

```markdown
## Diagnosis Complete

### Root Cause
[Summary of findings with evidence]

### Proposed Solution
[Architecture/design summary]

## Implementation Plan

### 1. Backend / Services
- [Task]

### 2. Database
- [Task]

### 3. Frontend / UI
- [Task]

### 4. Testing & Verification
- [Commands]

## Files Expected to Change
- `path/to/file1.py` — [Modify | New | Delete]

## Acceptance Criteria
- [ ] Observable evidence 1
- [ ] Observable evidence 2

---
**No application code has been modified yet.**
**Plan saved to:** `implementation_plan/YYYY-MM-DD_..._v1.md`
Please confirm if you approve this plan so I may begin execution.
```

**In `[AWAITING_CONFIRMATION]` state, the agent MUST NOT:**
- Edit source files
- Run database migrations
- Delete or move files
- Make speculative changes

---

## Stage 9 — Record Approval

After explicit user approval, update the implementation document:

```markdown
Status:          Approved
Approval Status: Approved
Approved By:     User
Approval Date:   YYYY-MM-DD
```

Do not fabricate approval. If approval is ambiguous, ask for confirmation.

---

## Stage 10 — Implement (Only After Approval)

1. Follow the approved plan milestone by milestone.
2. **Do NOT silently expand scope.**
3. **Do NOT silently redesign architecture.**
4. **Do NOT silently fix unrelated problems.**

If a newly discovered issue materially changes the plan:
```
STOP → Explain → Update Gap Analysis → Update Plan → Save v2 → Request Approval Again
```

Minor incidental fixes required for the approved feature to function may be made, but must be documented as deviations.

---

## Stage 11 — Update README.md

After every substantial implementation, ask:

> "Did this change alter any project knowledge that belongs in README.md?"

README triggers:
- New/changed/deleted feature
- New/changed route or endpoint
- New/changed API contract
- Database table or field changes
- Storage key changes
- Environment variable changes
- Configuration changes
- Workflow changes
- Integration changes
- Authentication/authorization changes
- New scripts or utilities
- Deployment changes
- Troubleshooting procedures

### README Absolute Rules
1. **Read the current README fully** before making any change.
2. **Never replace a comprehensive README with a simplified one** that loses existing information.
3. If README has 500 lines and the change needs 20 new lines, add 20 lines — do not regenerate 150 lines.
4. Keep README as the **living technical booklet / encyclopedia / knowledge base** of the entire project.

---

## Stage 12 — Mandatory Testing

Testing is **non-negotiable**. Never claim tests passed without running them.

### Minimum Required Verification (UAIC-specific)
```bash
# Backend tests (157 tests, 100% pass)
cd backend && .venv\Scripts\pytest --tb=short -q

# Backend linter (0 errors)
.venv\Scripts\ruff check app tests

# Frontend TypeScript (0 errors)
cd frontend && npx tsc --noEmit

# PowerShell AST syntax (0 errors)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# Docker Compose validation
docker compose config
```

### Test Report Format
```text
Command:     [exact command]
Environment: [local / CI]
Date:        YYYY-MM-DD
Result:      PASS / FAIL
Tests:       X passed, Y failed, Z skipped
Warnings:    [any]
```

### Failed Tests — Never Hide
```text
Initial Test: FAILED
Root Cause:   [What caused it]
Fix:          [What was changed]
Retest:       PASSED
```

---

## Stage 13 — Validate & Regression Check

Verify:
- [ ] User request 100% fulfilled
- [ ] Approved plan followed
- [ ] Acceptance criteria satisfied (with observable evidence)
- [ ] No regressions in existing functionality
- [ ] Security rules intact (no unmasked secrets, no disabled auth)
- [ ] All tests passing
- [ ] README synchronized with actual implementation
- [ ] Zero IDE/Pyrefly problems across all workspace files
- [ ] Enterprise UI pages span full viewport (`w-full max-w-none flex-1`) with unified `<Navbar />`
- [ ] PowerShell scripts remain persistent and interactive

---

## Stage 14 — Final Documentation in `implementation_plan/`

Create or update final documents under `implementation_plan/`:

| Document Type | Contents |
|---|---|
| `implementation-plan` | Requirements, scope, architecture, acceptance criteria |
| `gap-analysis` | Current vs expected, gaps found, action taken |
| `walkthrough` | Actual implemented flow (not just the plan) |
| `change-log` | File-by-file changes, deviations, reasons |
| `test-report` | Commands, results, failures, fixes, retest |
| `validation` | Acceptance evidence, regression results, known issues |

### Storage of Verification Recordings & Visual Artifacts
- **Mandatory Homes**:
  - `implementation_plan/Recording/`: Strictly for all browser subagent video recordings (`.webp`).
  - `implementation_plan/Images/`: Strictly for all UI verification and inspection screenshots (`.png`).
- Media files MUST be cleanly separated into these two folders so they are version-controlled with the repository rather than kept solely in the transient IDE brain directory.
- All markdown walkthroughs and audit records must link directly to `Recording/<filename>.webp` or `Images/<filename>.png`.

### Document Statuses
```
Proposed | Awaiting Approval | Approved | In Progress | Implemented |
Testing | Validated | Complete | Rejected | Superseded | Corrected | Archived
```

### Dynamic AI Verification Status
When the full automated testing suite (100%) and visual evidence (recordings/screenshots) have executed and passed:
`**AI Verification:** Complete (100% Automated Testing Suite)`

> **Mandatory Rule:** Never leave completed deliverables with stale statuses such as `Approved - In Execution`, `Completed - Pending Human Verification`, or `Awaiting Human Verification`. Once the automated testing suite and visual evidence collection pass, the document status must be finalized as `Complete` with `**AI Verification:** Complete (100% Automated Testing Suite)`.

---

## Stage 15 — Finalize Deliverables & Verification Reporting

After implementation is complete and all automated tests have passed:

1. Update the document status in `implementation_plan/` to `Complete` with:
   `**AI Verification:** Complete (100% Automated Testing Suite)`.
2. Verify all browser video recordings are stored in `implementation_plan/Recording/` (`.webp`) and inspection screenshots in `implementation_plan/Images/` (`.png`).
3. Report test results and links to created/updated files in `implementation_plan/`.

```text
AI implementation is complete.
AI Verification: Complete (100% Automated Testing Suite)

Documents updated in implementation_plan/:
- [file 1]
- [file 2]

Visual Evidence:
- Recordings: implementation_plan/Recording/
- Screenshots: implementation_plan/Images/
```

---

## Stage 16 — Move to Permanent History (Only After Human Verification)

Only after the user says: *"Verified"*, *"Approved"*, *"Move them"*, *"Documentation is correct"*, *"Finalize"*:

1. Check for naming conflicts.
2. Preserve previous versions.
3. Do not overwrite historical documents.
4. Confirm files correspond to the actual implementation.
5. Report exactly what was moved.

**NEVER automatically delete history to hide errors. Use `Superseded`, `Rejected`, `Archived` instead.**

---

## Document Versioning

When a plan materially changes, create a new version:

```
v1 — Initial plan
v2 — Updated after security gap discovered
v3 — Final approved implementation
```

### Revision History (in documents)
```markdown
## Revision History

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1 | 2026-09-05 | Initial plan | Initial diagnosis |
| v2 | 2026-09-05 | Added auth | Security gap found |
```

---

## Emergency Bypass Handling

If the user explicitly says: *"Skip confirmation"*, *"Fix it right now"*, *"Proceed without confirmation"*:

The agent may bypass `[AWAITING_CONFIRMATION]`. However it **MUST still**:
1. Rapidly inspect and diagnose.
2. Maintain database safety (never silently drop data).
3. Execute all tests.
4. Validate that the fix caused no regressions.
5. Create documentation in `implementation_plan/` afterward.
6. Ask for human verification of documentation.

---

## Implementation Quality Checklist

### Before Showing Plan
```
[ ] User request understood
[ ] Repository fully inspected
[ ] README.md read and understood
[ ] implementation_plan/ history reviewed
[ ] Existing implementation understood
[ ] Root cause identified (with evidence)
[ ] Gap analysis completed
[ ] Requirements defined
[ ] Scope and out-of-scope defined
[ ] All affected files/modules identified
[ ] Security considerations addressed
[ ] Testing strategy defined
[ ] Acceptance criteria are measurable
[ ] Plan saved to implementation_plan/
[ ] Plan matches what is shown to user
[ ] Approval explicitly requested
```

### Before Declaring Implementation Complete
```
[ ] Approved plan followed
[ ] No unauthorized scope expansion
[ ] README.md updated
[ ] All tests executed and passing
[ ] Regression check complete
[ ] Acceptance criteria verified with evidence
[ ] Deviations documented
[ ] Final documentation created in implementation_plan/
[ ] User notified to verify documentation
[ ] No secrets exposed
[ ] No fabricated test results
[ ] No false claims of completion
```

---

## The 28 Golden Rules

1. Inspect before modifying.
2. Diagnose before fixing.
3. Review README before substantial work.
4. Review implementation history before substantial work.
5. Create a detailed plan before implementation.
6. Save the plan to `implementation_plan/`.
7. Show the plan to the user.
8. Wait for explicit approval.
9. Never fabricate approval.
10. Implement only approved scope.
11. Test actual implementation with real commands.
12. Never fabricate test results.
13. Perform regression checks.
14. Keep README as the complete, living project booklet.
15. Never destroy useful existing README information.
16. Update README whenever project knowledge changes.
17. Maintain API, route, database, storage, workflow, and configuration documentation.
18. Maintain implementation history.
19. Document deviations from the approved plan.
20. Never hide failures — preserve history with `Rejected`, `Superseded`, `Archived`.
21. Keep AI documentation in `implementation_plan/` and store media strictly in `implementation_plan/Recording/` and `implementation_plan/Images/`.
22. Upon passing the full automated test suite (100%) and visual validation, set document status to `Complete` and AI Verification to `Complete (100% Automated Testing Suite)`.
23. Never automatically move/delete `implementation_plan/` records.
24. Never delete history to hide mistakes.
25. Keep documentation synchronized with actual implementation.
26. Use measurable acceptance evidence — not vague statements.
27. Never claim work was completed without evidence.
28. Never leave completed tasks in `Approved - In Execution`, `Completed - Pending Human Verification`, or `Awaiting Human Verification`.

---

## Final Report Format

```markdown
## Implementation Complete

### Implementation ID
IMP-YYYY-MMDD-NNN

### What Was Implemented
[Concise summary]

### Files Changed
| File | Change | Reason |
|------|--------|--------|
| path/to/file | Modified | [Reason] |

### Documentation Created
- `implementation_plan/YYYY-MM-DD_..._implementation-plan_v1.md`
- `implementation_plan/YYYY-MM-DD_..._test-report_v1.md`
- `implementation_plan/YYYY-MM-DD_..._validation_v1.md`

### Visual Evidence
- Recordings: `implementation_plan/Recording/`
- Screenshots: `implementation_plan/Images/`

### README Updates
[What was added/updated and why]

### Test Results
| Test | Command | Result |
|------|---------|--------|
| Unit Tests | `pytest -q` | ✅ 270/270 passed |
| Linter | `ruff check` | ✅ 0 errors |
| TypeScript | `tsc --noEmit` | ✅ 0 errors |
| PowerShell Syntax | `check_ps1_syntax.ps1` | ✅ 0 errors |

### Acceptance Criteria
- [x] Evidence 1
- [x] Evidence 2

### Deviations from Plan
[Any deviations and reasons]

### Known Gaps / Follow-up Items
[Anything intentionally unresolved]

---
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Visual Evidence Preserved In:** `implementation_plan/Recording/` & `implementation_plan/Images/`  
**Implementation Record:** `implementation_plan/`  
```

---

## Stage 17 — Mandatory Task Completion & Error Resolution

1. **Complete Every Task Fully:** Do not mark a task as completed merely because the implementation was partially added. Verify that the requested functionality actually works end-to-end.
2. **Never Silently Skip:** If execution crashes, times out, or a dependency/build fails, perform a gap analysis and **resume from the last successful point**. 
3. **No Error Left Behind:** Before reporting completion, you MUST explicitly check the browser Developer Console (for unhandled promises, React errors, network failures) and the Terminal (for build errors, lint errors, test failures). Fix all root causes.
4. **Document Unresolved Blockers:** If an error cannot be immediately resolved due to external dependencies, document the exact error, root cause, impact, and recommended next action.
5. **The Non-Negotiable Definition of Done:** `Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked`.

---

## Global Engineering & File Management Standards

1. **Zero Duplicate Files Rule:** Never create multiple files with the same name or for the same purpose in different directories.
2. **Strict DRY Principle:** Extract reusable components, utility functions, or shared modules instead of duplicating functionality.
3. **Exception to Default Skills:** If the user explicitly specifies a custom path (e.g., "Store file in root"), you must place the file *exactly* where requested and nowhere else, overriding default skill behaviors.
4. **Verification Before Modification:** Before deleting or renaming, verify dependencies across the codebase (imports, Docker configs, scripts) and update them simultaneously.
5. **Clean Code & Comments:** Every file MUST include a top-level Docstring/Header. Complex logic/regex MUST include inline comments explaining *why*.
