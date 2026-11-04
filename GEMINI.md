# GEMINI.md â€” Project Guidelines for Gemini CLI & Antigravity
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
- Backend: `cd backend && .venv\Scripts\pytest -q`
- Lint: `cd backend && .venv\Scripts\ruff check app tests`
- Frontend Type Check: `cd frontend && npx tsc --noEmit`
- Frontend Lint: `cd frontend && npm run lint`
- PowerShell Syntax: `powershell -File scripts/check_ps1_syntax.ps1`

## Mandatory Pre-Completion Quality Gate (PERMANENT - IMP-2026-1031-002)
Before declaring ANY task complete, ALL of these must pass with zero errors:
1. ruff check - 0 errors
2. pytest - 0 failed
3. tsc --noEmit - 0 TypeScript errors
4. npm run lint - no warnings or errors
5. PS1 syntax check - all scripts 0 errors
6. IDE Problems panel - 0 diagnostics, 0 spelling errors
7. All .ps1 files pure ASCII (no em-dashes or multi-byte punctuation)
8. docker compose config - parses without errors
Never fabricate results. Show actual command output.

## Canonical Directory Rules (IMP-2026-1031-002)
- Recordings: docs/recordings/ (Zero recordings directly in docs/).
- Screenshots & Frames: docs/frames/.
- Documentation Images: docs/images/.
- Scripts: scripts/.
- End-to-End Tests: e2e/.
- Protected directories: anticaptcha-plugin_v0.83/, .agents/.

