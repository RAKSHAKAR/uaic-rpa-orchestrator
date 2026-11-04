# UAIC Project Rules — AI Engineering OS Quick-Reference

> **Source:** Extracted from `AGENTS.md §8` — do not duplicate; refer to AGENTS.md for authoritative governance prose.
> **Format:** Structured checklist for fast AI session enforcement.
> **Last Updated:** 2026-11-03

---

## MUST DO ✅

### Before Any Change
- [ ] Read `.agent/PROJECT_CONTEXT.md` for fast session bootstrap
- [ ] Read `AGENTS.md` for full governance rules
- [ ] Follow `diagnose-plan-confirm-execute` lifecycle: Understand → Inspect → Diagnose → Gap Analysis → Plan → Save to `docs/` → Show User → **Wait Approval** → Implement → Test → Validate → Document
- [ ] Run full automated test suite after any backend change: `pytest`, `ruff check`
- [ ] Run `tsc --noEmit` after any TypeScript change
- [ ] Run `scripts\check_ps1_syntax.ps1` after any `.ps1` change
- [ ] Save every substantial implementation plan to `docs/` BEFORE showing user

### Naming Conventions
- [ ] Implementation ID format: `IMP-YYYY-MMDD-NNN`
- [ ] Plan naming: `YYYY-MM-DD_uaic_<feature>_<doc-type>_v<N>.md`
- [ ] Place all plans in `docs/` (never loose in root)
- [ ] Place all scripts in `scripts/` or `backend/app/scripts/`

### Quality Gates (All Must Pass)
- [ ] G1: Requirements understood
- [ ] G2: Repository and architecture inspected
- [ ] G3: Appropriate skills selected
- [ ] G4: Implementation plan prepared
- [ ] G5: Change approval obtained where necessary
- [ ] G6: Code implemented
- [ ] G7: `ruff check` — 0 errors
- [ ] G8: `pytest` — 0 failed
- [ ] G9: Integration tests passed
- [ ] G10: `tsc --noEmit` — 0 TypeScript errors
- [ ] G11: `npm run lint` — 0 errors
- [ ] G12: `check_ps1_syntax.ps1` — 0 errors
- [ ] G13: `docker compose config` — parses without errors
- [ ] G14: Documentation updated
- [ ] G15: IDE diagnostics reviewed
- [ ] G16: Release readiness verified

### Code Standards
- [ ] Target Python **3.14.7** across all backend code
- [ ] Preserve synchronous Playwright browser automation (do NOT convert to async)
- [ ] Settings must persist in DB via `get_system_settings_async()`
- [ ] All secrets must be masked in API responses and logs
- [ ] All `.ps1` files must be pure ASCII (no em-dashes or multi-byte punctuation)

### Architecture Preservation
- [ ] Preserve state routing logic (FL/TX/Cross-State)
- [ ] Preserve fuzzy cascade (Claimant → Insured → Driver @ 0.60)
- [ ] Preserve DOL date base (1899-12-30, never change)
- [ ] Preserve claim number prefix rule (9-digit → prefix with "0")
- [ ] Preserve portal output schemas (especially NO CaseType for Harris JP + Harris Clerk)
- [ ] Preserve all existing API endpoints (no renames, no deletions)
- [ ] Preserve Celery task signatures in `scraper_tasks.py` and `fuzzy_tasks.py`

### UI Standards
- [ ] Use `w-full max-w-none flex-1` for enterprise full-width layouts
- [ ] Include unified `<Navbar />` on all primary routes
- [ ] Never use `alert()` for notifications in frontend
- [ ] Theme tokens from Branding page (never hardcode colors in components)

### Data Safety
- [ ] Never delete production data, audit history, or user records without explicit authorization + verified backup
- [ ] Never flush shared Redis instances without understanding ownership
- [ ] Never interpret "clean everything" as permission to destroy persistent history

### Documentation
- [ ] Maintain `README.md` as comprehensive authoritative booklet (never simplify)
- [ ] Save browser recordings (.webp) to `docs/recordings/`
- [ ] Save screenshots (.png) to `docs/frames/` or `docs/images/`
- [ ] Update `.agent/CHANGELOG.md` after every substantial task

---

## MUST NOT DO ❌

### Development Rules
- ❌ Do not modify source code before presenting a detailed plan and receiving explicit user confirmation
- ❌ Do not implement without explicit user approval (NO APPROVAL = NO IMPLEMENTATION)
- ❌ Do not mark documentation as `Human Verified` — only the user can do that
- ❌ Do not fabricate test results, approvals, verifications, or deployment status
- ❌ Do not leave completed tasks with stale statuses (`Approved - In Execution`, `Completed - Pending Human Verification`)

### Architecture Rules
- ❌ Do not delete, rename, or purge protected directories: `anticaptcha-plugin_v0.83/`, `.agents/`
- ❌ Do not add CaseType to Harris JP or Harris County Clerk scrapers
- ❌ Do not break Celery task signatures in `scraper_tasks.py` / `fuzzy_tasks.py`
- ❌ Do not replace browser automation with direct HTTP requests
- ❌ Do not skip CAPTCHA wait logic
- ❌ Do not hold DB transactions open during browser automation
- ❌ Do not hardcode credentials or API keys

### Code Quality Rules
- ❌ Do not create unnecessary stray files in project root
- ❌ Do not disable linters, spell checkers, or type checks to hide errors
- ❌ Do not suppress warnings without documented justification
- ❌ Do not replace a comprehensive README with a simplified version

### UI Rules
- ❌ Do not artificially constrain enterprise layouts with fixed max-widths (`max-w-6xl`, `max-w-4xl`)
- ❌ Do not allow PowerShell setup scripts to auto-exit after launching services
- ❌ Do not use System/OS theme detection (`prefers-color-scheme`) — Light/Dark only

---

## Approval Thresholds

| Change Type | Approval Required |
|---|---|
| New `.md` documentation file | NO |
| New test file | NO |
| Bug fix (low-risk, reversible) | YES — plan required |
| New feature | YES — plan required |
| Database schema change | YES — plan + backup required |
| API endpoint change | YES — plan required |
| Scraper modification | YES — plan required |
| Production deployment | YES — explicit authorization |
| Data deletion / cleanup | YES — backup + explicit authorization |
| Dependency update | YES — compatibility review |

