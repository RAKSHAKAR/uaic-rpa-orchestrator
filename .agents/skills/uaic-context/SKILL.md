---
name: uaic-orchestrator-context
description: |
  Complete context for working with the UAIC Claim & RPA Orchestrator codebase.
  Provides architectural knowledge, business rules, test commands, and contribution
  guidelines for any AI tool (Claude, Codex, Gemini, Cursor, etc.).
  Use this skill when making any code change to this repository.
---

# UAIC Orchestrator — AI Skill

## When to Use This Skill

Use this skill before making ANY change to the UAIC Orchestrator repository.
Read it fully before writing or modifying code.

## Strict Directory Structure Preservation & Hygiene Rules

1. **Exact Directory Layout Enforcement**:
   - The repository layout documented in `README.md` must be preserved at all times.
   - **DO NOT create stray or unnecessary files/folders** in the root directory (e.g. no loose `.db`, `.py`, `.csv`, `.xlsx`, `.bat`, or temporary test dumps in root).
   - All utility, scratch, diagnostic, and export verification scripts MUST be located in [`scripts/`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/) or [`backend/app/scripts/`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/scripts/).
   - All browser failure screenshots must go to `backend/screenshots/`.
   - All generated asynchronous export packages must go to `backend/exports/`.

2. **Protected Directories (NEVER DELETE OR RENAME)**:
   The following directories must NEVER be deleted, modified without permission, or removed by cleanup scripts:
   - `anticaptcha-plugin_v0.83/` — Chrome Manifest v3 AntiCaptcha solver extension
   - `.agents/` — AI engineering governance protocols, skills, and rules
   > *Note: `implementation_plan/`, `PowerAutomateSolutions/`, and `Testing files/` were intentionally removed in IMP-2026-1001-001.*

3. **Master Project Booklet (`README.md`)**:
   - `README.md` is the authoritative single-source booklet for the entire platform.
   - Whenever any new route, script, storage key, API endpoint, or configuration changes, `README.md` MUST be updated to reflect it immediately.

## Key Files to Read First

1. `AGENTS.md` — Business rules, API contracts, critical DO/DON'T rules
2. `README.md` — Authoritative project booklet, full architecture & directory layout
3. `backend/app/services/fuzzy_engine.py` — RapidFuzz cascade logic
4. `backend/app/automation/base.py` — BasePortalScraper + CAPTCHA flow
5. `backend/app/core/config.py` — Pydantic settings model
6. `frontend/src/types/index.ts` — All TypeScript types
7. `frontend/src/lib/api.ts` — Typed API client

## Before Any Change

1. Run `cd backend && .venv\Scripts\pytest -q` — must pass all 556 tests (2 org-policy skips are pre-existing)
2. Run `cd backend && .venv\Scripts\ruff check app tests` — must be clean (0 errors)
3. Run `cd frontend && npx tsc --noEmit` — must be 0 TypeScript errors
4. Check `AGENTS.md` section 8 (AI Agent Rules)

## Adding a New API Endpoint

1. Create handler in `backend/app/api/v1/endpoints/{module}.py`
2. Register in `backend/app/api/v1/router.py`
3. Add TypeScript type to `frontend/src/types/index.ts`
4. Add method to `frontend/src/lib/api.ts`
5. Write test in `backend/tests/test_api.py`

## Adding a New Portal Scraper

1. Create `backend/app/automation/{state}/{portal_name}.py`
2. Inherit from `BasePortalScraper` in `backend/app/automation/base.py`
3. Implement `search()` method — use existing scraper as template
4. Register in `backend/app/automation/__init__.py`
5. Add portal to state routing in `backend/app/tasks/scraper_tasks.py`
6. Add portal settings to `backend/app/services/settings_service.py`
7. Write scraper test in `backend/tests/test_scrapers.py`

## Modifying Business Rules

**NEVER change these without explicit confirmation:**
- State routing matrix (FL/TX/cross-state)
- DOL date serial base (1899-12-30)
- Fuzzy match cascade order (Claimant → Insured → Driver)
- Claim number prefix rule (9-digit gets "0" prefix)
- Portal output schemas (especially Harris JP/Harris Clerk = NO CaseType)

## Settings Architecture

All runtime configuration flows through `SystemSettings`:
- Stored in DB via `settings_service.py`
- Workers read via `get_system_settings_async()`
- Frontend displays via `/api/v1/settings`
- Never hardcode values that should be in Settings

## Secret Handling

- All credentials masked in API responses and logs
- Never log `anticaptcha_api_key`, `guidewire_api_key`, `miami_password`
- Settings API returns `configured: true` + masked value for secrets

## Browser Automation & Engine Rules

- Supports **Chromium** (Playwright bundled, recommended default), **Google Chrome** (host binary with profile seeding), and **Microsoft Edge** (Edge channel).
- Multi-engine configuration managed in `SystemSettings` (`browser_engine`).
- Google Chrome: uses profile seeding from `%LOCALAPPDATA%\Google\Chrome\User Data` with `developer_mode: true` to avoid `--load-extension` sideloading block.
- Keep browser open across all portals for one claim.
- Never close browser between tabs in same claim session.
- CAPTCHA: click → wait for extension → verify token/DOM change → continue.

## Mandatory Task Completion & Error Resolution Rules

1. **Complete Every Task Fully**: Never consider a task complete just because code was written. Verify end-to-end functionality.
2. **No Error Left Behind**: Before declaring completion, you MUST inspect:
   - **Browser Developer Console**: Check for unhandled promise rejections, React errors, broken asset links, and failed API calls.
   - **Terminal Logs & Runtime**: Check for compilation warnings, build failures, lint violations, and CORS errors. Fix the root cause of every error.
3. **Interruption Recovery**: If execution is interrupted by timeouts, context limits, terminal errors, or crashes, perform a gap analysis against requirements and resume from the last successful checkpoint. Never silently skip tasks.
4. **Definition of Done**:
   `Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked`

## Mandatory Final Verification Steps (Always Run Last)

Before declaring any engineering task complete, ALWAYS execute and verify:
1. **Zero IDE / Pyrefly Problems**: Check `@[current_problems]`; verify zero syntax/indentation/import errors. Clean up any temporary scratch/test scripts that trigger virtual diagnostics.
2. **Full-Width Enterprise UI Standard**: Verify all UI routes (`/`, `/settings`, `/branding`, `/monitor`, `/health`, `/exceptions`, `/upload`) render at 100% viewport width (`w-full max-w-none flex-1`) with the unified `<Navbar />`.
3. **Persistent PowerShell Orchestrator (`setup.ps1` / `setup_local.ps1`)**: Verify setup scripts never auto-close and offer interactive options. Run syntax verification with `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"`.
4. **Docker Compose Validation**: Run `docker compose config` to guarantee that all YAML services, volume mounts (`./anticaptcha-plugin_v0.83:/app/anticaptcha-plugin_v0.83`), and environment configurations remain valid.
5. **Backend Test Suite**: `cd backend && .venv\Scripts\pytest -q` (all 182 tests: 172 passed, 10 skipped when Redis/MailDev offline).
6. **Backend Linter**: `cd backend && .venv\Scripts\ruff check app tests` (clean, 0 errors).
7. **Frontend Type Check & Build**: `cd frontend && npx tsc --noEmit && npm run build` (zero errors).



## Mandatory 15 Master Governance & Quality Rules (IMP-2026-1031-003)

Every AI assistant or engineer contributing to this repository MUST strictly abide by these 15 rules:
1. **Inspect current implementation before changing anything**: Examine existing settings, configuration services, browser automation architecture, Celery queues, concurrency controls, portal scrapers, and documentation. Never assume a feature is missing or broken without verifying.
2. **Respect the existing solution architecture**: Do not rebuild working systems. Target Python 3.14, FastAPI, Playwright sync sessions, Redis, and Next.js 14 App Router without architectural degradation.
3. **Verify settings propagation end to end**: Confirm settings flow seamlessly: Settings Page → API → Database → Configuration Service → Celery Task → Browser Engine → Portal Scraper.
4. **Verify browser compatibility**: Support Google Chrome, Microsoft Edge, and Playwright Chromium with genuine binary resolution and version detection. Never silently switch engines.
5. **Verify extension loading and configuration**: Ensure Anti-Captcha extension loads in dedicated profiles with pre-synchronized API keys and toolbar pinning across all Chromium browsers.
6. **Stop execution when mandatory browser prerequisites fail**: If extension loading or browser initialization fails, fail-fast with BLOCKED_EXTENSION_INITIALIZATION and dispatch an actionable IT Support notification. Never continue silently.
7. **Never falsely report CAPTCHA success**: Verify genuine DOM tokens (cf-turnstile-response, g-recaptcha-response, .antigate_solver_solved) before continuing.
8. **Validate actual GUI/headless behavior**: Attended mode must open a visible browser with authentic human pacing and cursor movement; Headless mode must run in the background. Never claim visible interaction occurred in headless mode.
9. **Verify all portal routing and dispatch rules**: Route FL claims to 3 bots (Broward, Hillsborough, Miami-Dade), TX claims to 5 bots (Travis, Dallas, Harris JP, Harris Clerk, Harris District), and cross-state claims to all 8 bots concurrently. Quarantine missing/ambiguous state claims to NEEDS_REVIEW.
10. **Investigate the full IDE Problems panel**: Methodically resolve all real TypeScript, Python, ESLint, and import errors.
11. **Fix spelling and encoding problems**: Maintain pure UTF-8 without BOMs, resolve legitimate spelling errors, and register verified domain terms into cspell.json.
12. **Resolve browser console and terminal errors**: Guarantee zero unhandled promise rejections, React errors, failed API calls, CORS failures, or Celery startup crashes.
13. **Run relevant regression and E2E tests**: Execute backend pytest and frontend Playwright test suites to guarantee 100% pass rates.
14. **Verify diagrams and charts remain visible**: Prevent auto-polling re-renders from unmounting diagrams, flowcharts, 9-stage steppers, and chart SVG rings. Ensure resilient fallback tracks.
15. **Provide actual execution evidence before claiming completion**: Embed verifiable command outputs, automated test logs, and authentic WebP recordings before marking any task complete.

## Canonical Artifact & Directory Governance (IMP-2026-1031-002)
- Execution recordings: docs/recordings/ (Zero recordings directly in docs/).
- Screenshots and extracted frames: docs/frames/.
- Images and visual documentation assets: docs/images/.
- All executable project scripts: scripts/.
- All E2E testing implementation and test-related artifacts: e2e/.
- Technical, functional, architecture and operational documentation: docs/.
- Protected directories: anticaptcha-plugin_v0.83/ and .agents/.
