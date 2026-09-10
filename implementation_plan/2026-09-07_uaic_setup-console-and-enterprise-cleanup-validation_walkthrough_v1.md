# Walkthrough: Setup Console Infrastructure Fix & Enterprise Cleanup Alignment

**Document ID:** `DOC-2026-0907-001-WLK`  
**Implementation ID:** `IMP-2026-0906-003`  
**Date:** September 7, 2026  
**Status:** `IMPLEMENTED — AWAITING HUMAN VERIFICATION`  
**Implementation Record:** [`2026-09-07_uaic_setup-console-and-enterprise-cleanup-validation_implementation-record_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-07_uaic_setup-console-and-enterprise-cleanup-validation_implementation-record_v1.md)  
**Prior Walkthrough:** [`walkthrough.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/walkthrough.md) (Sep 6, IMP-2026-0906-002)

---

## 1. What Was Done & Why

This walkthrough covers the Sep 7, 2026 continuation of `IMP-2026-0906-003` — the approved plan to fully validate all Setup Console options [1]-[9]+[M]+[0] and align the Enterprise Cleanup Engine to the 18-category specification.

### Problem the User Reported

After the Sep 6 implementation, running Option [1] (Start All Services) still left infrastructure ports showing as `[STOPPED]` in the Live Status Monitor (Option [9]):

```
[STOPPED]  MailDev Web Inspector   (Port 1080)
[STOPPED]  MailDev SMTP Server     (Port 1025)
[STOPPED]  Redis Queue Broker      (Port 6379)
[STOPPED]  PostgreSQL Database     (Port 5432)
```

The application services (Frontend 3000, FastAPI 8000, Flower 5555) launched fine — only the Docker infrastructure services were broken.

---

## 2. Fix 1 — Infrastructure Startup (setup_local.ps1)

### The Exact Bug

```powershell
# BEFORE — broken code in Invoke-StartAllServices:
docker start uaic_postgres uaic_redis uaic_maildev 2>$null | Out-Null
docker compose up -d postgres redis maildev 2>$null | Out-Null
Start-Sleep -Seconds 2
Write-LogMessage "Infrastructure containers active." "SUCCESS"
```

Three problems:
1. `2>$null | Out-Null` — silenced everything including download progress and errors
2. `Start-Sleep -Seconds 2` — on first run, images must be downloaded (takes minutes, not seconds)
3. No confirmation — the script printed "Infrastructure containers active" even when nothing was running

### The Fix

```powershell
# AFTER — smart three-phase startup:

# Phase 1: Warn if this is a first-time pull
$existingImages = docker images --format "{{.Repository}}:{{.Tag}}" 2>$null
if ($existingImages -notcontains "postgres:16-alpine" ...) {
    Write-LogMessage "Pulling Docker images (first-time setup, may take a few minutes)..." "WARNING" "Yellow"
}

# Phase 2: docker compose up WITH visible output (no suppression)
docker compose up -d postgres redis maildev

# Phase 3: Health polling — wait up to 60 seconds for ports to listen
$waited = 0
while ($waited -lt 60) {
    Start-Sleep -Seconds 2; $waited += 2
    $pgReady = (Get-NetTCPConnection -LocalPort 5432 -ErrorAction Ignore) -ne $null
    $rdReady = (Get-NetTCPConnection -LocalPort 6379 -ErrorAction Ignore) -ne $null
    $mdReady = (Get-NetTCPConnection -LocalPort 1080 -ErrorAction Ignore) -ne $null
    if ($pgReady -and $rdReady -and $mdReady) { break }
    # Every 10s: PostgreSQL:OK, Redis:waiting, MailDev:waiting
}
Write-LogMessage "All infrastructure containers are healthy and listening." "SUCCESS"
```

### Result Confirmed

After the fix, `docker compose up` was run and all images pulled and containers started:
```
Container uaic_postgres  Started
Container uaic_redis     Started
Container uaic_maildev   Started
```

Docker `ps` confirmed all 3 containers healthy on ports 5432, 6379, 1080/1025.

---

## 3. Fix 2 — 18-Category Cleanup Engine (clean_history.py)

### The Bug

`MENU_CATEGORIES` in `clean_history.py` had 15 entries instead of the required 18. The category keys were also inconsistent with `cleanup_service.py`:

| # | Old Menu | Correct Menu |
|---|---------|-------------|
| 9 | `error_screenshots` | `bot_history` |
| 10 | ❌ Missing | `dashboard_metrics` |
| 11 | ❌ Missing | `run_history` |
| 15 | `all_operational` | `all_operational` |
| 16 | ❌ Missing | `redis_runtime` (was #14) |
| 17 | ❌ Missing | `all_operational` |
| 18 | ❌ Missing | `all_supported` |

### The Fix

Updated `MENU_CATEGORIES` to exactly 18 entries matching `ORDERED_CATEGORY_KEYS` in `cleanup_service.py`:

```python
MENU_CATEGORIES = [
    ("claims",                "Claim & Automation Data"),
    ("queue",                 "Work Queue Data"),
    ("court_cases",           "Scraped Court Case Data"),
    ("fuzzy_matches",         "Fuzzy Match Data"),
    ("guidewire_activities",  "Guidewire Activity Data"),
    ("notifications",         "Outbound Notification Data"),
    ("notification_deliveries","Notification Delivery History"),
    ("telemetry",             "Execution Telemetry & Audit Logs"),
    ("bot_history",           "Bot / Scraper Execution History"),      # was error_screenshots
    ("dashboard_metrics",     "Dashboard / Analytics Data"),           # NEW
    ("run_history",           "Application Run History"),              # NEW
    ("app_logs",              "Application Logs"),
    ("scraper_logs",          "Scraper Logs & Browser Artifacts"),
    ("temp_caches",           "Temporary Files & Build Caches"),
    ("generated_exports",     "Generated Export Files"),
    ("redis_runtime",         "Redis Runtime & Celery Broker Queues"),
    ("all_operational",       "All Operational Data Categories"),
    ("all_supported",         "All Supported Data Categories"),        # NEW
]
```

Also fixed:
- `clear_database_records()` legacy helper: `error_screenshots` → `bot_history`
- Select-all shortcut: `"15"` → `"17"`, `"18"`

---

## 4. Fix 3 — Ruff Lint (conftest.py)

```python
# BEFORE (2 lint errors):
import gc
import sys        # F401: unused
import pytest     # I001: missing blank line before third-party

# AFTER (clean):
import gc         # stdlib

import pytest     # third-party (blank line separator added)
```

---

## 5. Full Verification Matrix

| Check | Result |
|-------|--------|
| `pytest -q` (182 tests) | ✅ 182 passed, 0 failed, 0 warnings |
| `ruff check app tests` | ✅ All checks passed (0 errors) |
| `npx tsc --noEmit` | ✅ 0 errors |
| `npm run lint` | ✅ 0 errors (1 warning OK per AGENTS.md) |
| `npm run build` | ✅ 10/10 routes built |
| `scripts\check_ps1_syntax.ps1` | ✅ 0 errors (setup.ps1, setup_local.ps1, check_ps1_syntax.ps1) |
| `docker compose config --quiet` | ✅ VALID |
| Docker containers | ✅ postgres, redis, maildev — all healthy |

---

## 6. What Still Needs Human Verification

> [!CAUTION]
> The following must be verified by the human user before this can be marked HUMAN VERIFIED:

1. **Option [1] Live Test**: Start Docker Desktop → run `setup_local.ps1` → Option [1] → confirm all 7 ports show `[RUNNING]` in Option [9]
2. **Option [3] Category Count**: Run Option [3] → confirm exactly 18 categories appear in the numbered menu
3. **Option [7] Clean Diagnostics**: Run Option [7] → confirm `182 passed, 0 warnings, 0 errors`

---

## 7. Governance Notes

- All documentation for this implementation is saved in `implementation_plan/` per AGENTS.md rules
- The walkthrough in `implementation_plan/walkthrough.md` covers Sep 5-6 work; this file covers Sep 7 additions
- No documentation was left exclusively in the transient IDE brain directory

| Document | Path |
|----------|------|
| Approved Plan (Sep 6) | `implementation_plan/2026-09-06_uaic_setup-console-and-enterprise-cleanup-validation_implementation-plan_v1.md` |
| Implementation Record (Sep 7) | `implementation_plan/2026-09-07_uaic_setup-console-and-enterprise-cleanup-validation_implementation-record_v1.md` |
| This Walkthrough (Sep 7) | `implementation_plan/2026-09-07_uaic_setup-console-and-enterprise-cleanup-validation_walkthrough_v1.md` |
