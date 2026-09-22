# IMP-2026-0922-001 — E2E Live Test Plan
## Upload → Extraction → Guidewire: Fleet 1 & 2

**Implementation ID:** IMP-2026-0922-001  
**Date:** 2026-09-21  
**Status:** Awaiting User Approval

---

## Executive Diagnosis

Before we can even start extraction, a **critical pre-condition failure** exists:

> [!CAUTION]
> The Settings database is **completely empty** — no AntiCaptcha API key, no Guidewire credentials, no concurrency limit, no browser mode. Without settings, the bots will fail immediately. **Settings must be configured first.**

### Current System State
| Component | Status |
|-----------|--------|
| FastAPI (port 8000) | ✅ RUNNING |
| Next.js (port 3000) | ✅ RUNNING |
| Redis (port 6379) | ✅ RUNNING |
| Flower (port 5555) | ✅ RUNNING |
| Settings in DB | ❌ EMPTY — must configure |
| AntiCaptcha API Key | ❌ NOT SET |
| Guidewire URL/Auth | ❌ NOT SET |
| Celery Worker | ✅ Python processes active |

### Test Files Confirmed
| File | Location |
|------|----------|
| `sample_claims - Florida.xlsx` | `Testing files\sample_claims - Florida.xlsx` |
| `5RecordsTexas.xlsx` | `Testing files\5RecordsTexas.xlsx` |

---

## Open Questions (Need Your Input)

> [!IMPORTANT]
> **Q1 — AntiCaptcha API Key:** What is the AntiCaptcha API key to use? (The key in `AntiCaptcha-Key.txt` in the plugin folder, or a different one?)
>
> **Q2 — Guidewire Auth:** What auth type and credentials to use for Guidewire in this test? (Bearer token / Basic / ApiKey / OAuth2) — or should Guidewire push be disabled during extraction tests and only enabled for final push verification?
>
> **Q3 — Clean DB before test?** There are currently 19 claims in DB (7 NEW, 2 IN_PROGRESS, 4 completed). Should I clear all records before the fresh E2E test, or keep existing data?
>
> **Q4 — Chrome path:** Is Chrome installed at the default `C:\Program Files\Google\Chrome\Application\chrome.exe`? The browser launch test in Settings will confirm this.

---

## Proposed Changes / Test Phases

---

### Phase 0 — Pre-Flight: Settings Configuration (via UI)

Navigate to `http://localhost:3000/settings` and configure ALL sections live in browser:

#### 0A. Automation & API Keys
- **AntiCaptcha API Key** → enter key from `anticaptcha-plugin_v0.83/AntiCaptcha-Key.txt`
- **Browser Mode** → `Attended GUI` (headful, visible Chrome windows)
- **Parallel RPA Concurrency** → `1` for Phase 1, then change to `2` for Phase 2
- **Chrome Path** → verify or set to `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **Run "Setup AntiCaptcha Extension"** button → pins extension to toolbar
- **Run "Test Browser Launch"** → confirms Chrome opens with green AntiCaptcha icon

#### 0B. Guidewire Configuration
- **Guidewire API URL** → from `.env`: `https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate`
- **Auth Type** → set as per credentials provided
- **Enable Guidewire Push** → toggle ON
- **Run "Test Guidewire Connection"** → must return success before proceeding

#### 0C. Fuzzy Match Settings
- **Min Filing Date** → `2010-01-01` (per business rules)
- **Fuzzy Threshold** → `0.60`

#### 0D. Verify Health Dashboard
- Navigate to `http://localhost:3000/health`
- Confirm all 8 portals are reachable (green ping)
- Confirm AntiCaptcha, Redis, Celery all healthy

---

### Phase 1 — Fleet=1 Test: Florida Claims (`sample_claims - Florida.xlsx`)

**Concurrency setting: 1 (only 1 Chrome at a time)**

#### Step 1.1 — Upload
- Navigate to `http://localhost:3000/upload`
- Drag-drop `Testing files/sample_claims - Florida.xlsx`
- Preview parsed rows — verify DOL dates, claimant names, policy states
- Click **Import** → claims enter DB as `NEW`

#### Step 1.2 — Dashboard Verify
- Navigate to `http://localhost:3000`
- Confirm Florida claims appear in table with state = `FL`
- Confirm status = `NEW`
- Note: State routing for FL-only claims → Broward + Hillsborough + Miami portals only

#### Step 1.3 — Select & Start (fleet=1)
- Select all Florida claims → click **Bulk Start**
- Expected: **1 Chrome window opens**, remaining claims queued as `NEW`
- Monitor dashboard: claim 1 moves `NEW → SCRAPING_IN_PROGRESS`
- Monitor logs: `[SingleSessionRunner] AntiCaptcha fully configured: 37-key config injected`
- Watch Chrome: AntiCaptcha icon should be **green/active** in toolbar
- Observe portal navigation: Broward → Hillsborough → Miami

#### Step 1.4 — Queue Monitor
- Navigate to `http://localhost:3000/monitor`
- Watch sequential processing — as claim 1 completes, claim 2 starts automatically
- Confirm no 2nd Chrome window opens while claim 1 is active

#### Step 1.5 — Post-Extraction Review
- Claims should show `MATCH_FOUND`, `NO_MATCH_FOUND`, or `MANUAL_REVIEW`
- Click into each claim detail → review portal results (Broward/Hillsborough/Miami JSON)
- If `MANUAL_REVIEW` → go to `/exceptions` to approve/reject fuzzy matches

#### Step 1.6 — Guidewire Push (Florida)
- For completed claims → click **Push to Guidewire**
- Expected: `200 OK` from Guidewire API
- Claim status → `COMPLETED`
- Verify: claim number rule applied (9-digit gets '0' prefix)

---

### Phase 2 — Fleet=2 Test: Texas Claims (`5RecordsTexas.xlsx`)

**Change concurrency to 2 via Settings page first.**

#### Step 2.1 — Settings: Change Fleet to 2
- Navigate to `http://localhost:3000/settings`
- Change **Parallel RPA Concurrency** → `2`
- Save settings

#### Step 2.2 — Upload Texas File
- Navigate to `http://localhost:3000/upload`
- Upload `Testing files/5RecordsTexas.xlsx`
- Verify TX state claims, DOL dates parsed correctly
- Import → 5 claims enter DB as `NEW`

#### Step 2.3 — Select & Start (fleet=2)
- Select all 5 Texas claims → **Bulk Start**
- Expected: **2 Chrome windows open simultaneously**
- Claims 3–5 remain `NEW`, picked up by queue runner
- Confirm: 3rd window does NOT open while 2 are active

#### Step 2.4 — Texas Portal Coverage
- State routing: TX + TX = Harris Clerk + Dallas + Harris JP + Harris District + Travis (5 portals)
- Watch both Chrome windows navigate different portals in parallel
- Monitor Queue Monitor for 2 concurrent SCRAPING_IN_PROGRESS

#### Step 2.5 — Post-Extraction and Guidewire Push (Texas)

---

### Phase 3 — Cross-State Test (Bonus, if time allows)

If Florida policy + Texas loss location (or vice versa), ALL 8 portals run. Verify from any cross-state claim in the existing data.

---

## Known Blockers & Anticipated Issues

| # | Blocker | Root Cause | Mitigation |
|---|---------|-----------|------------|
| B1 | **Settings empty** | Settings never saved to DB | **Must configure via Settings page before any test** |
| B2 | **AntiCaptcha key missing** | Not set in DB | Enter key in Settings → test connection |
| B3 | **Guidewire credentials unknown** | Not in .env or DB | User must provide — or disable push and test extraction only |
| B4 | **Court portals may block/CAPTCHA** | Live court websites have anti-bot | AntiCaptcha extension handles this — key must have balance |
| B5 | **Portal timeouts** | Slow court website response | `PLAYWRIGHT_TIMEOUT_MS=30000` — may need increase for slow portals |
| B6 | **Celery worker not running** | No worker = tasks queue but never execute | Must confirm celery worker is active (`celery -A app.core.celery_app worker`) |
| B7 | **Chrome path mismatch** | Chrome not found at default path | Use "Test Browser Launch" in Settings to diagnose |
| B8 | **Claims stuck IN_PROGRESS** | Previous test run didn't clean up | Clear all records or use "Bulk Retry" first |

---

## Celery Worker Check (Critical)

> [!WARNING]
> The system shows Python processes running, but we must confirm a **Celery worker** is active — not just FastAPI. Without a Celery worker, tasks will queue in Redis but **never execute** and claims will stay `NEW` forever.
>
> If Celery worker is not running, we must start it:
> ```powershell
> cd backend
> .venv\Scripts\celery -A app.core.celery_app worker --loglevel=info --concurrency=2 -Q scraper,fuzzy,ingest,default
> ```

---

## Execution Order

```
Phase 0: Settings Config → Test Browser → Test AntiCaptcha → Test Guidewire
  ↓ (all green)
Phase 1: Upload Florida → Start fleet=1 → Watch extraction → Push Guidewire
  ↓ (all claims completed)
Phase 2: Change fleet=2 → Upload Texas → Start → Watch 2 Chromes → Push Guidewire
  ↓
Document: Screenshots, recordings, logs → implementation record
```

---

## Verification Plan

- **Browser recording:** Entire session recorded via browser subagent (WebP video)
- **Screenshots:** Settings page, upload preview, dashboard, claim detail, Guidewire response
- **Logs:** Backend `uvicorn` logs for AntiCaptcha injection confirmation, concurrency gate messages
- **Recordings saved to:** `implementation_plan/Recording/`
- **Screenshots saved to:** `implementation_plan/Images/`

---

## What I Need From You Before Starting

1. **Your AntiCaptcha API key** (or confirm I can use `anticaptcha-plugin_v0.83/AntiCaptcha-Key.txt`)
2. **Guidewire auth credentials** — or confirm: test extraction only, skip Guidewire push
3. **DB clean?** — clear all 19 existing claims, or keep them?
4. **Confirm Celery worker is running** in a separate terminal

> [!NOTE]
> If you just want to see extraction working and skip the actual Guidewire push (since that's a live production endpoint), I can disable push and just verify the payload is correctly generated.
