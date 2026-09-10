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

2. **Protected User Directories (NEVER DELETE OR RENAME)**:
   The following 5 folders must NEVER be deleted, modified without permission, or removed by cleanup scripts:
   - `implementation_plan/` — Reference prompts, architecture roadmaps & implementation plans
   - `PowerAutomateSolutions/` — Legacy Power Automate solution packages, Robin binaries, BRDs & screen recordings
   - `Testing files/` — User-supplied court benchmark spreadsheets and test datasets
   - `anticaptcha-plugin_v0.83/` — Chrome Manifest v3 AntiCaptcha solver extension
   - `.agents/` — AI engineering governance protocols, skills, and rules

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

1. Run `cd backend && .venv\Scripts\pytest -q` — must pass 157 tests
2. Run `cd backend && .venv\Scripts\ruff check app tests` — must be clean
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

## Mandatory Final Verification Steps (Always Run Last)

Before declaring any engineering task complete, ALWAYS execute and verify:
1. **Zero IDE / Pyrefly Problems**: Check `@[current_problems]`; verify zero syntax/indentation/import errors. Clean up any temporary scratch/test scripts that trigger virtual diagnostics.
2. **Full-Width Enterprise UI Standard**: Verify all UI routes (`/`, `/settings`, `/branding`, `/monitor`, `/health`, `/exceptions`, `/upload`) render at 100% viewport width (`w-full max-w-none flex-1`) with the unified `<Navbar />`.
3. **Persistent PowerShell Orchestrator (`setup.ps1` / `setup_local.ps1`)**: Verify setup scripts never auto-close and offer interactive options (start services in attended GUI vs unattended headless, stop services, clean run history, install deps, purge deps, diagnostics). Run syntax verification with `powershell -NoProfile -Command "Get-Content setup.ps1 | Out-Null; Get-Content setup_local.ps1 | Out-Null; Write-Output 'PowerShell scripts parse OK'"`.
4. **Docker Compose Validation**: Run `docker compose config` to guarantee that all YAML services, volume mounts (`./anticaptcha-plugin_v0.83:/app/anticaptcha-plugin_v0.83`), and environment configurations remain valid.
5. **Backend Test Suite**: `cd backend && .venv\Scripts\pytest -q` (all 157 tests passing).
6. **Backend Linter**: `cd backend && .venv\Scripts\ruff check app tests` (clean, 0 errors).
7. **Frontend Type Check & Build**: `cd frontend && npx tsc --noEmit && npm run build` (zero errors).

