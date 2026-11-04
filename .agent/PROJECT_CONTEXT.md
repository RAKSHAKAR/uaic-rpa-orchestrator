# UAIC Project Context — AI Session Bootstrap

> **Purpose:** Fast-load project context for any new AI session. Read this first before touching any code.
> **Maintained by:** AI Engineering OS (`IMP-2026-1103-002`)
> **Last Updated:** 2026-11-03
> **Source of Truth:** AGENTS.md (governance), README.md (booklet), docs/ (reports)

---

## 1. Project Identity

**UAIC Claim & RPA Orchestrator** — Production-grade replacement for Microsoft Power Automate Desktop RPA bots that automate court-case discovery across 8 Florida/Texas county court portals, perform fuzzy-match deduplication, and push results to Guidewire Insurance Cloud.

**Release Status:** v1.0.0 RC — Executive sign-off achieved (`IMP-2026-1103-001`). 100-record acceptance test passed.

---

## 2. Repository Layout (Key Paths)

```
d:\scratch\Bot_UAIC\
├── .agent/                    ← AI OS hub (this directory)
├── .agents/skills/            ← 147 installed skill library (DO NOT MODIFY)
├── AI_WORKFLOW_LIBRARY/       ← 145-skill universal framework
├── anticaptcha-plugin_v0.83/  ← PROTECTED — Chrome MV3 extension
├── backend/
│   ├── .venv/                 ← Python 3.14.7 virtualenv
│   ├── orchestrator.db        ← Active SQLite database
│   ├── app/
│   │   ├── api/v1/endpoints/  ← FastAPI route handlers (audit, claims, health, ingest, matches, notifications, queue, settings)
│   │   ├── automation/        ← Playwright scrapers (florida/broward, hillsborough, miami; texas/dallas, travis, harris_jp, harris_district, harris_cclerk)
│   │   ├── core/              ← config.py, database.py, celery_app.py
│   │   ├── models/            ← SQLAlchemy ORM models
│   │   ├── schemas/           ← Pydantic validation schemas
│   │   ├── services/          ← excel_parser, fuzzy_engine, guidewire_client, settings_service, notification_service
│   │   ├── tasks/             ← Celery tasks (scraper, fuzzy, ingest, export, notification, retry, queue_runner)
│   │   └── scripts/           ← Utility scripts (NOT production code)
│   ├── tests/                 ← 562+ pytest tests (85 modules)
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── app/               ← Next.js 14 App Router pages (10 routes)
│       ├── components/        ← 19 shared React components
│       ├── lib/api.ts         ← Axios API client (typed)
│       └── types/index.ts     ← TypeScript types
├── docs/                      ← All documentation, reports, recordings, images
├── e2e/                       ← End-to-end test assets
├── scripts/                   ← 15 PowerShell utility scripts
├── v4_subflows/               ← Power Automate V4 Robin reference (authoritative)
├── exports/                   ← Generated export files
├── uploads/                   ← Uploaded claim files
├── AGENTS.md                  ← AI governance rules (READ FIRST)
├── GEMINI.md                  ← Gemini-specific rules
├── README.md                  ← Project booklet (authoritative)
├── docker-compose.yml
└── setup_local.ps1
```

---

## 3. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend | Next.js | 14.2 |
| Frontend | React + TypeScript | 18.3 + 5.x |
| Frontend | Tailwind CSS + Radix UI | 3.x + various |
| Frontend | TanStack Query/Table | 5.x / 8.x |
| Backend | FastAPI + Uvicorn | 0.115 |
| Backend | Python | 3.14.7 |
| Backend | Pydantic v2 + SQLAlchemy 2 | 2.9 + 2.0.35 |
| Worker | Celery + Redis + Flower | 5.4 + 7.2 + 2.0 |
| Database | SQLite (WAL) → Postgres path | 3.x |
| Automation | Playwright + Chrome | 1.48 + 131 |
| Matching | RapidFuzz | 3.6 |
| Testing | pytest + ruff | 8.3 + 0.6.9 |

---

## 4. Critical Business Rules (IMMUTABLE — Do Not Change)

### Rule 1 — State Routing
```python
if policy_state == loss_location_state:
    if policy_state == "FL":  portals = [broward, hillsborough, miami]
    elif policy_state == "TX": portals = [harris_cclerk, dallas, harris_jp, harris_district, travis]
else:  # Cross-state: run ALL 8
    portals = [broward, hillsborough, miami, harris_cclerk, dallas, harris_jp, harris_district, travis]
```

### Rule 2 — DOL Date Conversion
Excel serial dates use **1899-12-30** base, stored as **MM/dd/yyyy**. Never introduce timezone shifts.

### Rule 3 — Claim Number Prefix
If `len(claim_number) == 9`: prefix with `"0"`. Applied only to ClaimNumber in Guidewire payload.

### Rule 4 — Fuzzy Match Cascade (RapidFuzz partial_ratio, threshold=0.6)
```
1. Claimant (first + last) → CaseStyle
2. If no match: Insured (first + last) → CaseStyle
3. If no match: Driver (first + last) → CaseStyle
```
Minimum filing date: `>= 2010-01-01` (configurable in Settings).

### Rule 5 — Portal Output Schema (EXACT)
| Portal | Fields |
|---|---|
| Broward / Hillsborough / Miami / Dallas / Travis / Harris District | CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType |
| Harris JP / Harris County Clerk | CaseNumber, CaseStyle, FilingDate, CaseStatus (**NO CaseType**) |

### Rule 6 — Database Storage Keys
```
fl_jsonbody_broward, fl_jsonbody_hillsborough, fl_jsonbody_miami
te_jsonbody_cclerk, te_jsonbody_dallas, te_jsonbody_harris, te_jsonbody_hcdistrict, te_jsonbody_travis
```

---

## 5. API Conventions

- Base URL: `http://localhost:8000/api/v1/`
- All endpoints versioned under `/api/v1/`
- Pagination: `?page=1&page_size=20`
- Filters: query params per endpoint
- Auth: currently none (internal RPA tool — network-isolated deployment)
- Error format: `{"detail": "message"}` (FastAPI default)
- See AGENTS.md §5 for full endpoint catalogue

---

## 6. Frontend Routes

| Route | Purpose |
|---|---|
| `/` | Claims dashboard (main) |
| `/claims/:id` | Claim detail |
| `/upload` | File import |
| `/monitor` | Queue monitor |
| `/health` | System health |
| `/exceptions` | Fuzzy match review |
| `/settings` | Robot configuration |
| `/branding` | Brand & theme management |
| `/audit` | Audit trail |
| `/notifications` | Email console |

---

## 7. Design System

- **26 semantic CSS tokens** defined in `frontend/src/app/globals.css`
- **2 themes:** Light (`[data-theme="light"]`) and Dark (`.dark, [data-theme="dark"]`)
- **No system/OS detection** — user toggles manually; preference persisted in localStorage
- **Branding page** (`/branding`) is the authoritative source of truth for all token values
- See `.agent/DESIGN_SYSTEM_CONTEXT.md` for full token catalogue

---

## 8. Test Commands (Exact)

```powershell
# Backend unit & integration tests
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest tests --tb=short -q

# Backend E2E tests
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m pytest e2e/backend -o pythonpath=backend --tb=short -q

# Python lint (zero errors required)
d:\scratch\Bot_UAIC\backend\.venv\Scripts\python.exe -m ruff check app tests

# Frontend TypeScript (zero errors required)
Set-Location d:\scratch\Bot_UAIC\frontend; npx tsc --noEmit

# Frontend lint
Set-Location d:\scratch\Bot_UAIC\frontend; npm run lint

# Frontend production build
Set-Location d:\scratch\Bot_UAIC\frontend; npm run build

# PowerShell syntax check
powershell -NoProfile -ExecutionPolicy Bypass -File "d:\scratch\Bot_UAIC\scripts\check_ps1_syntax.ps1"

# Docker compose validation
docker compose -f d:\scratch\Bot_UAIC\docker-compose.yml config
```

---

## 9. Known Limitations (as of 2026-11-03)

1. **Travis County WAF** — HTTP 429 triggered at velocity >5 req/min per client IP. Handled via 600s cooldown + automatic re-dispatch.
2. **Hillsborough PerimeterX** — Bot challenge triggered by automated browser telemetry. Handled via 300s cooldown + HumanInteractionEngine.
3. **Dallas Turnstile** — Solver balance exhaustion possible. Handled via `CaptchaResolutionError` → `AWAITING_HUMAN` state.
4. **SQLite concurrency** — WAL mode mitigates but Postgres migration path exists via `backend/app/scripts/migrate_sqlite_to_postgres.py`.
5. **No authentication layer** — Designed for network-isolated enterprise deployment.

---

## 10. Key Reference Documents

| Document | Location | Purpose |
|---|---|---|
| Governance rules | `AGENTS.md` | AI agent operating rules (MUST READ) |
| Project booklet | `README.md` | Comprehensive reference |
| Stage/status definitions | `docs/Core Subsystem Operator Manuals/STAGE_AND_STATUS_DEFINITIONS.md` | Authoritative lifecycle states |
| 100-record acceptance report | `docs/UAIC_FINAL_100_RECORD_CROSS_STATE_ACCEPTANCE_REPORT.md` | Latest executive acceptance evidence |
| Release readiness | `docs/Implementation Reports/FINAL_RELEASE_READINESS_REPORT.md` | v1.0.0 RC sign-off |
| Architecture context | `.agent/ARCHITECTURE_CONTEXT.md` | Pure architecture reference |
| Skill registry | `.agent/PROJECT_SKILL_REGISTRY.md` | Task → skill routing index |
| Task routing matrix | `.agent/TASK_ROUTING_MATRIX.md` | 27-category routing table |

