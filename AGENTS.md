# UAIC Claim & RPA Orchestrator — AI Agent Context File

> **This file is for AI assistants (Claude, Codex, Gemini, GPT-4, Cursor, etc.)**
> It provides critical architectural context so any AI tool can immediately contribute without re-discovering the codebase.

---

## 1. Project Identity

**UAIC Claim & RPA Orchestrator** — production-grade replacement for Microsoft Power Automate Desktop RPA bots that automate court-case discovery across 8 Florida/Texas county court portals, perform fuzzy-match deduplication, and push results to Guidewire Insurance Cloud.

**Stack:** Next.js 14 + Python 3.14 + FastAPI + Celery + Redis + SQLAlchemy + Playwright + RapidFuzz

---

## 2. Repository Layout

```
Bot_UAIC/
├── backend/                   # Python FastAPI + Celery worker
│   ├── app/
│   │   ├── api/v1/endpoints/  # FastAPI route handlers
│   │   │   ├── claims.py      # All claim CRUD + bulk ops + export
│   │   │   ├── health.py      # /health + /health/detailed + portal ping
│   │   │   ├── ingest.py      # Excel/CSV upload & preview
│   │   │   ├── matches.py     # Fuzzy match review
│   │   │   ├── queue.py       # Queue start/pause/retrigger
│   │   │   └── settings.py    # Settings CRUD + Guidewire/Portal test
│   │   ├── automation/
│   │   │   ├── base.py        # BasePortalScraper + CAPTCHA handling
│   │   │   ├── browser_manager.py  # ChromeSession, TabManager, ExtensionManager
│   │   │   ├── session_runner.py   # Orchestrates multi-tab Chrome session
│   │   │   ├── florida/
│   │   │   │   ├── broward.py
│   │   │   │   ├── hillsborough.py
│   │   │   │   └── miami.py
│   │   │   └── texas/
│   │   │       ├── dallas.py
│   │   │       ├── travis.py
│   │   │       ├── harris_jp.py
│   │   │       ├── harris_district.py
│   │   │       └── harris_cclerk.py
│   │   ├── core/
│   │   │   ├── config.py      # Pydantic Settings (env vars)
│   │   │   ├── database.py    # SQLAlchemy async engine + session
│   │   │   └── celery_app.py  # Celery app + queues definition
│   │   ├── models/
│   │   │   ├── claim.py       # ClaimRecord ORM model
│   │   │   ├── court_case.py  # ScrapedCourtCase ORM model
│   │   │   └── match_result.py# FuzzyMatchResult ORM model
│   │   ├── services/
│   │   │   ├── excel_parser.py    # openpyxl/pandas ingestion (1899-12-30 dates)
│   │   │   ├── fuzzy_engine.py    # RapidFuzz claimant→insured→driver cascade
│   │   │   ├── guidewire_client.py# GuidewireClient (Bearer/ApiKey/Basic/OAuth2)
│   │   │   └── settings_service.py# SystemSettings DB persistence
│   │   └── tasks/
│   │       ├── scraper_tasks.py   # Celery tasks for browser automation
│   │       ├── fuzzy_tasks.py     # Celery tasks for matching + Guidewire
│   │       ├── ingest_tasks.py    # Celery tasks for file parsing
│   │       ├── queue_runner.py    # Auto-queue sequential runner
│   │       └── retry_tasks.py     # Retry failed/stuck claims
│   └── tests/                 # 107 tests, all passing
├── frontend/                  # Next.js 14 App Router
│   └── src/
│       ├── app/
│       │   ├── page.tsx           # Main Dashboard (claims table, stats, bulk ops)
│       │   ├── health/page.tsx    # /health — Operational health dashboard
│       │   ├── monitor/page.tsx   # /monitor — Queue monitor
│       │   ├── settings/page.tsx  # /settings — Full settings UI
│       │   ├── upload/page.tsx    # /upload — Excel/CSV import
│       │   ├── exceptions/page.tsx# /exceptions — Fuzzy review
│       │   └── claims/[id]/page.tsx # /claims/:id — Claim detail
│       ├── components/
│       │   ├── CommandPalette.tsx  # Ctrl+K global command palette
│       │   ├── ResponsiveShell.tsx # Root layout shell
│       │   ├── Sidebar.tsx         # Desktop nav sidebar
│       │   ├── Navbar.tsx          # Top navigation bar
│       │   ├── MobileBottomNav.tsx # Fixed mobile bottom nav
│       │   ├── FileUploader.tsx    # Drag-drop file upload with preview
│       │   └── StatusBadge.tsx     # Status badge component
│       ├── lib/api.ts             # Axios API client (all endpoints typed)
│       └── types/index.ts         # All TypeScript types
├── PowerAutomateSolutions/    # Legacy Power Automate reference (V4 is authoritative)
│   └── BotCreation_1_0_0_7/
│       ├── customizations.xml     # All workflow definitions
│       └── desktopflowbinaries/   # Robin language desktop flow definitions
└── implementation_plan/       # Reference prompts and implementation plans
```

---

## 3. Critical Business Rules (DO NOT CHANGE)

### State Routing Logic
```python
if policy_state == loss_location_state:
    if policy_state == "FL":  portals = [broward, hillsborough, miami]
    elif policy_state == "TX": portals = [harris_cclerk, dallas, harris_jp, harris_district, travis]
else:  # Cross-state: run ALL 8
    portals = [broward, hillsborough, miami, harris_cclerk, dallas, harris_jp, harris_district, travis]
```

### DOL Date Conversion
Excel serial dates use **1899-12-30** base, stored as **MM/dd/yyyy**. Never introduce timezone shifts.

### Claim Number Rule
If `len(claim_number) == 9`: prefix with `"0"`. Applied only to ClaimNumber in Guidewire payload.

### Fuzzy Match Cascade (RapidFuzz partial_ratio, threshold=0.6)
```
1. Claimant (first + last) → CaseStyle
2. If no match: Insured (first + last) → CaseStyle
3. If no match: Driver (first + last) → CaseStyle
```
Minimum filing date: `>= 2010-01-01` (configurable in Settings).

### Search Count Derivation (DualSearch / TripleSearch)
| Scenario | DualSearch | TripleSearch |
|---|---|---|
| All same | 1 | 1 |
| Insured = Driver, Claimant ≠ | 1 | 3 |
| Insured = Claimant, Driver ≠ | 2 | 1 |
| Driver = Claimant, Insured ≠ | 2 | 1 |
| All different | 2 | 3 |

### Portal Output Schema (EXACT — do not add/remove fields)
| Portal | Fields |
|---|---|
| Broward/Hillsborough/Miami/Dallas/Travis/Harris District | CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType |
| Harris JP / Harris County Clerk | CaseNumber, CaseStyle, FilingDate, CaseStatus (**NO CaseType**) |

---

## 4. Database Storage Keys
```
fl_jsonbody_broward, fl_jsonbody_hillsborough, fl_jsonbody_miami
te_jsonbody_cclerk, te_jsonbody_dallas, te_jsonbody_harris, te_jsonbody_hcdistrict, te_jsonbody_travis
```

---

## 5. API Endpoints Summary

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health | Basic health |
| GET | /api/v1/health/detailed | Full system health (8 components + 8 portals) |
| GET/POST | /api/v1/health/portals/{key}/ping | Portal reachability test |
| GET | /api/v1/claims | List claims (paginated, filterable, sortable) |
| POST | /api/v1/claims | Create claim |
| GET | /api/v1/claims/{id} | Get claim detail |
| PUT | /api/v1/claims/{id} | Update claim |
| DELETE | /api/v1/claims/{id} | Delete claim |
| POST | /api/v1/claims/{id}/start | Start automation for claim |
| POST | /api/v1/claims/{id}/stop | Stop/cancel claim |
| POST | /api/v1/claims/{id}/push-guidewire | Push to Guidewire |
| POST | /api/v1/claims/{id}/run-bot/{key} | Run single portal bot |
| GET | /api/v1/claims/{id}/export | Export single claim (xlsx/csv/json/pdf) |
| GET | /api/v1/claims/stats | Aggregate stats |
| GET | /api/v1/claims/export | Bulk export |
| POST | /api/v1/claims/bulk-delete | Bulk delete |
| POST | /api/v1/claims/bulk-start | Bulk start |
| POST | /api/v1/claims/bulk-retry | Bulk retry |
| POST | /api/v1/claims/bulk-status | Bulk status change |
| POST | /api/v1/claims/clean | Clear all records |
| POST | /api/v1/ingest/upload | Upload Excel/CSV |
| POST | /api/v1/ingest/preview | Preview file before import |
| GET | /api/v1/matches/pending | Get pending fuzzy match reviews |
| POST | /api/v1/matches/{id}/review | Approve/reject match |
| POST | /api/v1/matches/unique-names | Deduplicate party names across 3 columns with 60% RapidFuzz matching |
| GET | /api/v1/queue/status | Queue health |
| POST | /api/v1/queue/start-all | Start queue runner |
| POST | /api/v1/queue/pause | Pause queue |
| POST | /api/v1/queue/retrigger | Retry failed claims |
| GET | /api/v1/queue/auto-mode | Auto-queue status |
| POST | /api/v1/queue/auto-mode | Toggle auto-queue |
| GET | /api/v1/settings | Get system settings |
| POST | /api/v1/settings | Save settings |
| POST | /api/v1/settings/reset | Reset to defaults |
| POST | /api/v1/settings/test-guidewire | Test Guidewire connection |
| POST | /api/v1/settings/test-portal | Test portal reachability |
| POST | /api/v1/settings/test-browser | Test Chrome launch (Attended GUI vs. Headless) |
| POST | /api/v1/settings/setup-extension | One-time AntiCaptcha extension configuration & toolbar pinning |
| POST | /api/v1/settings/email/test-connection | Test SMTP/Mock email provider connectivity & latency |
| POST | /api/v1/settings/email/test-send | Send interactive live test email |
| GET | /api/v1/notifications | Paginated notification delivery history log |
| GET | /api/v1/notifications/{id} | Single notification record detail |
| GET | /api/v1/notifications/templates | List notification email templates |
| GET | /api/v1/notifications/templates/{id}/preview | Dynamic HTML preview of notification template |
| GET | /api/v1/notifications/rules | List event trigger rules & recipient matrix |
| PUT | /api/v1/notifications/rules | Update event notification rules |

---

## 6. Frontend Routes

| Route | Component | Description |
|---|---|---|
| `/` | `app/page.tsx` | Main claims dashboard |
| `/claims/:id` | `app/claims/[id]/page.tsx` | Claim detail view |
| `/upload` | `app/upload/page.tsx` | File import |
| `/monitor` | `app/monitor/page.tsx` | Queue monitor |
| `/health` | `app/health/page.tsx` | System health |
| `/exceptions` | `app/exceptions/page.tsx` | Fuzzy match review |
| `/settings` | `app/settings/page.tsx` | Automation & Robot Configuration |
| `/branding` | `app/branding/page.tsx` | Brand & Identity Management Console |

---

## 7. Test Commands

```bash
# Backend tests (438 tests across 32 test suites)
cd backend
.venv\Scripts\pytest --tb=short -q

# Backend lint (zero errors)
.venv\Scripts\ruff check app tests

# Frontend TypeScript (0 errors)
cd frontend
npx tsc --noEmit

# Frontend lint (0 errors, some warnings OK)
npm run lint

# Frontend production build (all routes pass)
npm run build

# PowerShell syntax check (0 errors)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

---

## 8. AI Agent Rules When Modifying This Codebase

### MUST DO
- ✅ Follow the `diagnose-plan-confirm-execute` lifecycle: Understand → Inspect → Review README → Review History → Diagnose → Gap Analysis → Plan → Save to implementation_plan → Show User → Wait Approval → Implement → Test → Validate → Document → Human Verify
- ✅ **Definition of Done**: Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked
- ✅ **No Error Left Behind**: Check browser Developer Console (unhandled promises, React errors, failed API calls, CORS) and Terminal runtime logs (warnings, compilation, lint). Fix root causes before declaring completion
- ✅ **Interruption Recovery**: In the event of crashes, timeouts, context limits, or interruptions, perform gap analysis and resume from the last successful checkpoint without skipping
- ✅ Target **Python 3.14.7** across backend runtime and dependencies; preserve synchronous Playwright browser automation for Anti-Captcha extension stability
- ✅ Strictly preserve the repository directory layout documented in `README.md` and keep all 5 protected user folders intact (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`)
- ✅ Maintain `README.md` as the authoritative single-source booklet of the entire project (updating layout, routes, endpoints, storage keys, config — **never replace a comprehensive README with a simplified one**)
- ✅ Place all utility, scratch, diagnostic, and verification scripts into `scripts/` or `backend/app/scripts/` (never loose in root)
- ✅ Save every substantial implementation plan to `implementation_plan/` BEFORE showing it to the user (naming: `YYYY-MM-DD_uaic_<feature>_<doc-type>_v<N>.md`)
- ✅ Assign a unique Implementation ID (`IMP-YYYY-MMDD-NNN`) to every substantial task and cross-reference it in all related documents
- ✅ Ensure dynamic automated verification: upon completing work and running the full automated testing suite (pytest, ruff, tsc, ps1) with visual/video evidence, document status must be finalized as Complete with: `**AI Verification:** Complete (100% Automated Testing Suite)`
- ✅ Create a final implementation record (plan + change log + test report + validation) in `implementation_plan/` after every substantial task
- ✅ Save all browser subagent recordings (.webp) into `implementation_plan/Recording/` and all visual verification screenshots (.png) into `implementation_plan/Images/` (strictly separated, never leave them exclusively in the transient IDE brain directory)
- ✅ Run `pytest` after any backend change (416 tests across 31 test suites)
- ✅ Run `ruff check` after any Python change (0 errors)
- ✅ Run `tsc --noEmit` after any TypeScript change (0 errors)
- ✅ Run `scripts\check_ps1_syntax.ps1` after any `.ps1` change (0 errors)
- ✅ Inspect and resolve all IDE problems (`@[current_problems]`); verify zero Pyrefly virtual diagnostics or syntax errors
- ✅ Build full-width enterprise UI layouts (`w-full max-w-none flex-1`) with the unified `<Navbar />` on all primary routes
- ✅ PowerShell launcher (`setup_local.ps1`) must be persistent, interactive, and never auto-close unexpectedly
- ✅ Preserve all existing API contracts (do not rename endpoints)
- ✅ Preserve all business logic (state routing, fuzzy cascade, DOL date, claim number prefix)
- ✅ Keep portal output schemas EXACT (especially no CaseType for Harris JP + Harris Clerk)
- ✅ Settings must persist in DB and workers must read from `get_system_settings_async()`
- ✅ All secrets must be masked in API responses and logs
- ✅ Always validate `setup_local.ps1` and `docker-compose.yml` integrity as the final verification step before reporting completion

### MUST NOT DO
- ❌ Do not leave completed tasks with stale, intermediate, or pending statuses such as `Approved - In Execution`, `Completed - Pending Human Verification`, or `Awaiting Human Verification` after automated testing passes
- ❌ Do not create unnecessary, stray, or loose files/folders in the project root or scattered in the workspace
- ❌ Do not delete, rename, or purge any of the 5 protected user directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`)
- ❌ Do not modify source code before presenting a detailed plan and receiving explicit user confirmation
- ❌ Do not implement without explicit user approval of the plan (NO APPROVAL = NO IMPLEMENTATION)
- ❌ Do not mark documentation as `Human Verified` — only the user can do that
- ❌ Do not fabricate test results, approvals, verifications, or deployment status
- ❌ Do not replace an existing comprehensive README with a simplified version that loses existing information
- ❌ Do not create loose implementation documents outside `implementation_plan/`
- ❌ Do not silently fix unrelated problems — document them as follow-up gaps instead
- ❌ Do not artificially constrain enterprise page layouts with fixed max-widths (like `max-w-6xl` or `max-w-4xl`)
- ❌ Do not allow PowerShell setup scripts to auto-exit after launching services
- ❌ Do not hardcode credentials or API keys
- ❌ Do not change the serial date base (must stay 1899-12-30)
- ❌ Do not remove existing API endpoints
- ❌ Do not break Celery task signatures in `scraper_tasks.py` / `fuzzy_tasks.py`
- ❌ Do not add CaseType to Harris JP or Harris County Clerk scrapers
- ❌ Do not use `alert()` for notifications in frontend
- ❌ Do not replace browser automation with direct HTTP requests
- ❌ Do not skip CAPTCHA wait logic
- ❌ Do not hold DB transactions open during browser automation

---

## 9. Key Configuration Files

| File | Purpose |
|---|---|
| `backend/.env` | `DATABASE_URL`, `REDIS_URL`, `APP_ENV` |
| `backend/app/core/config.py` | Pydantic Settings model |
| `backend/app/services/settings_service.py` | DB-persisted system settings |
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL` |
| `docker-compose.yml` | Full stack Docker configuration |
| `setup_local.ps1` | Windows local dev launcher |

---

## 10. Power Automate Reference (V4 = Authoritative)

The `PowerAutomateSolutions/BotCreation_1_0_0_7/` directory contains the **V4** Robin desktop flow definitions. These are the behavioral reference. When V2/V3/V4 behaviors conflict, **V4 wins**.

Key V4 improvements over V3:
- Detailed latency benchmark dialogs
- Disabled aggressive Chrome termination between portals
- DOM token checking (`g-recaptcha-response`) for CAPTCHA success detection

---

## 11. Guidewire Payload Contract

```json
{
  "ClaimNumber": "0123456789",  // 9-digit gets '0' prefix
  "ExposureNumber": "001",
  "CaseItems": [
    {
      "CaseNumber": "...",
      "CaseStyle": "...",
      "CountyWebsite": "...",
      "SuitFiledDate": "..."
    }
  ]
}
```

---

## 12. AI Interoperability Notes

This file (`AGENTS.md`) is recognized by:
- **Claude** (Anthropic) — reads `AGENTS.md` / `CLAUDE.md` automatically
- **OpenAI Codex** / **ChatGPT** — reads `AGENTS.md` context files
- **Google Gemini / Antigravity** — reads `AGENTS.md` via customization system
- **Cursor** — reads `.cursor/rules` and `AGENTS.md`
- **GitHub Copilot** — reads repo context files

Any AI tool working on this codebase should read this file FIRST before making changes.

**Skills Directory:** `.agents/skills/` — contains reusable AI skill definitions:
- `.agents/skills/diagnose-plan-confirm-execute/SKILL.md` — **Universal Engineering Governance Skill** (73 rules). Full lifecycle: Understand → Inspect → Review README → Review History → Diagnose → Gap Analysis → Plan → Save to `implementation_plan/` → Show User → Wait Approval → Implement → Test → Validate → Update README → Document → Human Verify. NO APPROVAL = NO IMPLEMENTATION.
- `.agents/skills/theme-system/SKILL.md` — **Global Light & Dark Theme Governance Skill**. Exactly two application themes (Light and Dark only, zero System/OS detection). Centralized Branding Page is the authoritative single source of truth for 26 semantic color design tokens.
- `.agents/skills/uaic-context/SKILL.md` — Architectural knowledge, business rules, and test commands for this repository.

**Documentation System:**
- `implementation_plan/` — Direct home for all implementation plans, gap analyses, walkthroughs, and verified records
- `implementation_plan/ChatGPT_Prompt/` — Protected original prompt requirements
- `implementation_plan/README.md` — Documentation system guide (naming, IDs, lifecycle, anti-patterns)
- Implementation ID format: `IMP-YYYY-MMDD-NNN`
- Naming convention: `YYYY-MM-DD_uaic_<feature>_<doc-type>_v<N>.md`
