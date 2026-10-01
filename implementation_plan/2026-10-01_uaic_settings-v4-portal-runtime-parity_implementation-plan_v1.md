# Implementation Plan: Settings Runtime Integrity and Power Automate V4 Portal Parity

**Implementation ID:** IMP-2026-1001-002  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Settings, browser fleet, county automation, extraction, queue, integrations  
**Document Type:** Implementation Plan with Gap Analysis  
**Version:** v1  
**Status:** Approved  
**Created:** 2026-10-01  
**Last Updated:** 2026-10-01  
**AI Agent:** Codex  
**Approval Status:** Approved  
**Approved By:** User  
**Approval Date:** 2026-10-01  
**AI Verification:** Audit only; implementation and live portal verification pending

## 1. Request and acceptance contract

Make every operator control on `/settings` save reliably and govern the relevant application behavior. Reconcile all eight court bots and supporting workflows with the actual Power Automate V4 solution, including navigation, selectors, search, per-case detail visits, pagination, CAPTCHA, extraction, field mapping, status, persistence, and downstream matching. A CAPTCHA wait is an upper bound, with prompt continuation on a verified solve and portal-specific reset/retry after timeout. Completion requires measured end-to-end runs against all eight real court sites and truthful reporting of any site, credential, CAPTCHA, or environment blocker.

Preserve the protected business rules: FL/TX/cross-state routing; Excel date origin `1899-12-30`; 9-digit claim number prefix only in Guidewire payload; claimant/insured/driver matching cascade; exact four-field Harris JP and Harris County Clerk payloads, exact five-field payloads for the other six; all existing API paths and Celery signatures.

## 2. Authoritative evidence and current baseline

The source of truth is `PowerAutomateSolutions/BotCreation_1_0_0_7/customizations.xml`, Workflow ID `67dd091d-0ab9-4099-97af-47136f16ce4a` (V4 flow definition near XML line 3292), and its linked `desktopflowbinaries/b85f1bfd-d92b-4e25-ac23-a9e18e3d0606/data/ControlRepository_104c291e-5233-425c-bde4-e4db1c27a012.json`. Decoded Robin sections: launch 16-65; queue 66-85; Broward 87-167; Dallas 168-238; Travis 239-308; Harris JP 309-416; Harris Clerk 417-450; Miami 451-554; Harris District 555-602; Hillsborough 603-695; shared extraction driver 714-1466; error/failure routines 696-713 and 1467-1499. The complete solution also contains import, queue insertion, fuzzy/Guidewire, and failed-case retrigger cloud flows under `PowerAutomateSolutions/BotCreation_1_0_0_7/Workflows/`.

The working tree already had hundreds of edits and untracked files before this audit. Preserve them; inspect diffs before editing. Earlier implementation records claim 100% V4 parity, but their automated portal tests use mocked pages and cannot establish current live extraction. This plan supersedes that claim only where current code and V4 evidence prove a gap; it does not rewrite the historical records.

Baseline checks in this audit: `/settings` returned HTTP 200; `/api/v1/settings` returned HTTP 200; current API exposed four nonempty credential fields unmasked (values deliberately omitted here); Ruff passed; frontend `tsc --noEmit` passed; frontend lint passed. Thirty-seven targeted backend tests passed only after overriding the host's invalid `DEBUG=release` environment to `DEBUG=false`. **Test side effect:** `tests/test_settings_alignment.py::test_settings_save_and_retrieve_persistence` writes to the shared Redis settings key and calls reset; afterwards the live API and a separate backend process both returned repository defaults. The pre-test values were not captured, so prior custom values cannot be ruled out. Do not rerun shared-store settings tests. Use isolated Redis and a disposable database in implementation verification.

No actual county court extraction was executed in this audit. The CUA browser surface was unavailable. Current selectors, CAPTCHA solve latency, pagination completeness, and end-to-end case data remain unverified.

## 3. Confirmed gaps and root causes

| Priority | Current evidence | Required correction |
| --- | --- | --- |
| Critical | `backend/app/services/settings_service.py:179-275` uses Redis plus process-local fallback. Save and reset return success even when Redis write fails. `backend/app/api/v1/endpoints/settings.py:56-83` returns the full model. | Make the existing database settings table authoritative; make writes atomic and failure-visible; make workers load the same durable version. Mask secrets in responses and merge write-only secrets safely. |
| Critical | The live settings API returned nonempty AntiCaptcha, Miami, and Guidewire credentials without masking. `backend/app/schemas/settings.py:57,158-159,249-251` and `settings_service.py:43,61-62,119-121` also embed credential defaults. | Remove literal credential defaults, provide secure migration/retention of existing configured values, prevent API/log leakage, and test no plaintext response. |
| Critical | `backend/app/automation/texas/dallas.py:510-575`, `travis.py:513-578`, and `harris_jp.py:512-585` parse generic result cells but skip V4 `data-url` detail visits; V4 uses detail pages for Dallas CaseStyle, Travis CaseStyle/FilingDate, and Harris JP CaseStatus. | Implement V4 detail navigation and extraction with its control repository objects, then return to results safely. |
| Critical | `backend/app/automation/texas/harris_district.py:568-584` gets status from a table cell; V4 derives it from case-number text. Bots add `CountyWebsite`, `AccessLevel`, discovered headers, and invented field fallbacks to raw portal payloads. | Map V4 columns and detail objects exactly; emit only each portal's contracted four or five fields. Store provenance separately in ORM/audit fields. |
| Critical | `backend/app/automation/base.py:1082-1141` converts exhausted exceptions to `[]`; `backend/app/tasks/scraper_tasks.py:819-842` can call that `NO_MATCH_FOUND`. Existing cases are deleted at `:562-570` before new extraction succeeds; missing FilingDate is replaced with claim DOL at `:666-679`. | Distinguish verified empty results from failure, keep existing cases until a complete replacement succeeds, never invent a court filing date, and block matching/Guidewire for incomplete cases. |
| High | `backend/app/automation/base.py:785-1060` scans up to five seconds and then runs a fixed count of 500 ms polls, with no monotonic deadline. Miami ignores the returned post-submit CAPTCHA result at `miami.py:849-857`. | Apply an absolute per-challenge deadline, check immediately and then poll, cap each awaited operation by remaining time, and use one retry owner per portal. |
| High | `backend/app/automation/session_runner.py:607-627` overrides several configured portal URLs. `:599` caps initial navigation at 45 seconds despite 180-second UI allowance. `browser_manager.py:579-594` can overwrite configured AntiCaptcha toggles with defaults; `session_runner.py:435-507` compares only some toggles. | Honor validated V4-compatible URLs, configured timeout, and every extension switch in the launched browser. Reject unsupported URL overrides explicitly. |
| High | `backend/app/automation/base.py:503-605` defines action pacing/stealth helpers, but the eight bots do not call them. Numerous fixed waits and duplicate Playwright-plus-DOM submit clicks remain. | Route applicable actions through shared configured helpers, keep portal-specific event waits, and ensure exactly one submit per attempt. |
| High | `backend/app/tasks/scraper_tasks.py:399` fixes unique-name deduplication at 0.60 while the page exposes another value. `backend/app/tasks/retry_tasks.py:27-75` ignores auto-retry toggle/limit/delay; Celery retry declarations and delays are hardcoded; `queue.batch_chunk_size` is unused. | Reconcile V4's protected 60% dedup rule with the UI, enforce all queue settings in every retry path, and use chunk size or remove/label any nonfunctional control. |
| High | `backend/app/tasks/scraper_tasks.py:180-920` holds an async database session during browser work. `:616-624` silently caps old DOL to a rolling ten-year date, changing V4 search criteria. | Keep database transactions short; use actual claim DOL/V4 criterion and configured filing cutoff without silent substitution. |
| Medium | Portal ping uses direct HTTP rather than configured proxy; digest mode can create pending records without a confirmed delivery consumer; duplicate queue/automation concurrency fields diverge. | Validate and enforce those controls, unify concurrency precedence, and verify delivery/diagnostic behavior. |

## 4. V4 portal reconstruction matrix

| Portal | V4 actions and extraction that must be preserved | Current targeted work |
| --- | --- | --- |
| Broward | Party Name form; `firstName`, `lastName`, `filingDateOnOrAfterP`; `PersonSearchResults`; results td0 number, td1 style, td3 date, td4 status, td2 type; next-page and reset. V4 CAPTCHA block is explicitly disabled. | Verify actual form, pagination, exact five-field mapping, reset, and observed challenge behavior. |
| Dallas | Odyssey Smart Search `caseCriteria_SearchCriteria`; active bounded CAPTCHA/retry; nested result `data-url`; visit detail for CaseStyle, strip `[-\\/|]`; close detail/reset. | Add detail extraction, one submit, all pages, exact five fields. |
| Travis | Odyssey search and CAPTCHA; result `data-url`; visit detail for CaseStyle and FilingDate; close/reset. | Add detail extraction and exact five fields. |
| Harris JP | Odyssey search and CAPTCHA; result `data-url`; visit detail for CaseStatus; remove `Case Status`; paginate/reset. | Add detail extraction and exact four fields, no CaseType. |
| Harris County Clerk | First/last/date search; td0 number, td5 span style, td2 date, td1 status; Clear/reset. | Verify V4 deep-link or equivalent navigation, dates, pagination, exact four fields. |
| Miami-Dade | Login when needed; Party Name first/last/from-date; case cards for style/number/date/status/type; OCS Home and refresh reset. V4 CAPTCHA block is explicitly disabled. | Verify login/session, cards and pagination; handle a challenge if it actually appears per requested timeout contract without copying disabled V4 clicks. |
| Harris District | Search Our Records and Documents to Party Inquiry; `Last, First`, start date; td0 number, td1 strong style, td5 date, td6 type; status regex from number text; Search Again. | Correct status derivation and exact five fields. |
| Hillsborough | Party tab; `spFirstName`, `spLastName`, `spDateFiledAfter`; Search; no-data message; td2 number, td4 style, td6 date, td5 status, td7 type; close message/reset. | Verify modal dismissal, result mapping, pagination and exact five fields. |

V4's shared driver searches insured, then conditional driver and claimant according to DualSearch/TripleSearch, uses one Chrome session with eight tabs, and records per-portal statuses and JSON. Preserve this behavior and the current routing matrix. V4's disabled Broward/Miami CAPTCHA branches are historical facts; the user's explicit requirement to handle a challenge when one appears governs the modern runtime adaptation.

## 5. File-level implementation plan

### Phase A: durable, secure settings contract

- **Modify** `backend/app/services/settings_service.py`, `backend/app/models/guidewire.py` only if the existing `automation_settings` JSON row needs a version column, and database migration/config as required. Persist one validated settings document in the DB atomically; Redis becomes a cache. On database failure, reject save and stop new workers from using unknown defaults. Version and audit each successful update. Never silently normalize a saved URL on read.
- **Modify** `backend/app/schemas/settings.py` and `backend/app/api/v1/endpoints/settings.py`. Split internal settings from safe response/patch shapes, mask secret values, accept explicit secret replacement/clear operations, validate URL/engine combinations and cross-field constraints, and avoid technical error text or secrets in responses/logs. Preserve existing endpoint paths.
- **Modify** `frontend/src/app/settings/page.tsx`, `frontend/src/types/index.ts`, `frontend/src/lib/api.ts` only as needed for safe secret editing, actionable save errors, validated fields, effective-setting feedback, and queue/concurrency clarity. Reuse shared design tokens and current components; verify light/dark/mobile/keyboard behavior.
- **Add/modify tests** using isolated Redis and disposable DB for save/reload across processes, failed writes, concurrent updates, migration of current Redis values, secret masking, validation, and operator UI save/reset behavior. Snapshot current settings before any migration; do not run tests against the operator's store.

### Phase B: every visible control reaches its runtime consumer

- **Modify** `backend/app/tasks/scraper_tasks.py`, `backend/app/automation/base.py`, `browser_manager.py`, `session_runner.py`, and portal bots to apply every browser-fleet field. Snapshot settings at claim start; include a version in logs; use configured browser engine, mode, profile, extension directory, user agent, proxy, concurrency, page timeout, typing, pacing, clicks, CAPTCHA toggles, and backoff. Apply changed settings on the next claim without a worker restart.
- **Modify** `backend/app/tasks/queue_runner.py`, `retry_tasks.py`, `ingest_tasks.py`, relevant Celery task declarations and `core/celery_app.py` to enforce retry enable, maximum, delay, batch chunk size, and one authoritative concurrency value. Ensure periodic and immediate retry paths agree and do not dispatch duplicate claims.
- **Modify** matching, Guidewire, portal diagnostics, proxy, email/digest, and storage consumers where a rendered Settings control is currently ignored. Preserve the V4 claimant/insured/driver cascade and Guidewire payload. Add a field-by-field traceability test: UI key -> API schema -> durable row -> worker snapshot -> observable effect.
- **Open decision D1:** V4 and the protected repo rules use 60% for unique-name deduplication, while `/settings` exposes an adjustable threshold. Proposed default: preserve V4's 60% and make that value explanatory/read-only rather than pretending an arbitrary value affects production. If the user directs otherwise, revise the plan and matching tests before implementation.

### Phase C: bounded CAPTCHA and complete V4 extraction

- **Modify** `backend/app/automation/base.py` and eight portal modules. Start a monotonic deadline at challenge detection; check for solved state before sleeping; poll at a short bounded cadence; cap each wait by remaining time; return promptly when verified; time out at the configured maximum. On timeout, refresh/restart from that portal's V4 search entry state, refill criteria, and retry exactly as configured. Avoid nested retry loops and duplicate submits.
- **Modify** Dallas, Travis, Harris JP to visit V4 case-detail URLs and extract the missing fields. Correct Harris District status parsing and validate each portal's objects/selectors/navigation/pagination against the V4 control repository. Preserve portal-specific working behavior where it already matches V4.
- **Modify** `backend/app/tasks/scraper_tasks.py` and storage schemas/services only where needed. Use explicit `success_with_cases`, `verified_empty`, `failed`, and `blocked` outcomes. Validate the exact per-portal JSON contract and required fields. Keep provenance outside that JSON. Replace prior cases only after successful complete extraction in a short transaction. Do not substitute claim DOL for unknown filing date. Isolate one portal's failure without certifying it as a no-match result.
- **Modify** `README.md` after the code is verified: its current storage-key table describes extra Broward fields, its settings endpoint claims masked passwords, and its persistence description claims DB-backed settings despite current Redis-only behavior. Bring these statements into agreement with the tested implementation without simplifying the booklet.
- **Add/modify tests** with V4-derived DOM fixtures for each page and detail transition, multi-page extraction, no-data, CAPTCHA early solve, exact deadline, timeout/reload/restart/limit, partial failure, DB replacement, state routing, output schema, and Guidewire isolation.

### Phase D: real application and portal verification

- Start the actual app and worker in an isolated test configuration, then exercise `/settings` save/reload, each tab and diagnostic action, responsive layouts, light/dark, keyboard and accessibility, console/network logs. Do not alter the operator's current settings in QA.
- For each of the eight actual court portals, run a non-sensitive known test query through the application and worker, record entry URL, page objects, input values, submit count, CAPTCHA presence/elapsed time, page count, detail navigation, extracted rows, strict payload fields, DB rows, final bot status, matching result, and Guidewire mock payload. Compare fields with the V4 mapping and a known case record. Use the court's normal UI and configured solver; do not bypass security controls.
- Test attended and headless modes, supported engines, configured proxy on/off, one and multiple fleet slots, early solved and timeout CAPTCHA paths, and portal failures. A blocked/unavailable court or unavailable credential is a recorded failed acceptance item, never labeled a pass.
- Run full backend pytest, Ruff, frontend TypeScript/lint/build, PowerShell syntax, Docker Compose validation, browser visual/responsive/accessibility checks, and regression tests. Inspect critical console/network and worker errors. Validate `setup_local.ps1` and `docker-compose.yml` last. Save screenshots under `implementation_plan/Images/` and recordings under `implementation_plan/Recording/`, then update the comprehensive README and create change log, walkthrough, test report, and validation records under this Implementation ID.

## 6. Acceptance evidence required before Complete

1. A control inventory for every visible Settings field identifies its persisted key, reader, effect, negative case, and test result. Saving survives API/worker restart and Redis loss; failure cannot display false success.
2. GET/POST settings and application logs expose no plaintext credentials. Existing credentials survive an ordinary save of unrelated fields.
3. A configured 120-second CAPTCHA wait ends promptly on solve and never extends beyond the measured deadline except a documented scheduling tolerance; an unsolved challenge refreshes and restarts exactly within the configured attempt limit.
4. Every portal uses its V4 navigation/objects and extracts every required field across detail pages and pagination; only the exact four/five contracted keys enter each portal JSON payload.
5. Verified empty results stay distinct from failed/block/CAPTCHA outcomes; prior good cases are preserved on failure; unknown filing dates are not invented; incomplete cases cannot auto-push to Guidewire.
6. Eight real-site runs produce reviewable screenshots/recordings, redacted logs, and expected extracted case records. Any failed live site remains explicitly open, so the task is not declared fully complete.
7. Build, type check, lint, unit/integration/E2E, browser/responsive/theme/accessibility, console/network, PowerShell, and Docker checks pass after fixes, with exact commands/results recorded.

## 7. Risks, rollback, and scope control

- Court sites can change selectors, gate access, present CAPTCHA, or be unavailable. This is a live-validation risk, not grounds to fabricate parity. Record exact observed blockers and resume when access is available.
- The current Redis key may hold only defaults after the audit test described above. Before migration, export its then-current value securely for rollback and ask the operator to restore any known custom values. Never commit secrets or test data.
- Preserve the extensive pre-existing dirty working tree. Record a pre-change diff and use file-level edits; do not reset, clean, move, or delete protected folders.
- Keep existing API routes, task signatures, storage keys, claim routing, date base, matching cascade, and Guidewire contract. Any newly proven conflict with V4 or a protected business rule requires an updated plan and user decision.
- Rollback is a reviewed reversal of this task's specific code edits plus restoration of the captured settings document/database row. Do not roll back unrelated working-tree edits or discard post-migration user settings.

## 8. Approval checkpoint

The user approved this plan on 2026-10-01. Approval includes proposed decision D1: preserve the V4 60% unique-name deduplication rule and make the conflicting Settings control explanatory/read-only. Implementation and verification are in progress.
