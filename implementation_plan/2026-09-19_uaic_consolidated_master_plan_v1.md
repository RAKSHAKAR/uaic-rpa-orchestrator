# UAIC Claim & RPA Orchestrator — Consolidated Master Implementation Plan

**Implementation ID:** `IMP-2026-0919-MASTER`
**System Target:** UAIC Claim & RPA Orchestrator — Full Stack
**Date:** 2026-09-19
**Version:** v1 (Master Consolidation)
**Governing Skill:** `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`

---

## Background

This document synthesizes all outstanding issues, bugs, and feature gaps identified across the entire conversation history that have NOT yet been fully implemented and verified. Each item below is a discrete, testable scope.

---

## Issue Inventory (Pending Implementation)

| # | Category | Severity | Status |
|---|---|---|---|
| 1 | Claim Logs — "All" Unified Tab | UX Enhancement | Not Implemented |
| 2 | Telemetry Audit — Start/End Time Display | Bug Fix | Not Implemented |
| 3 | Fleet Concurrency — Multiple Browsers Bug | Critical Bug | Not Implemented |
| 4 | Monitor Table — "No. of Cases Extracted" Column | UX Enhancement | Not Implemented |
| 5 | AntiCaptcha Plugin Settings — Checkbox Toggles | Feature Gap | Not Implemented |
| 6 | AntiCaptcha Extension — Not Loaded During Extraction | Critical Bug | Not Implemented |

---

## Open Questions

> [!IMPORTANT]
> **Q1 — Fleet Semaphore Strategy:** The queue_runner already limits dispatch of Celery tasks by `max_concurrent_claims`. However, Celery workers run concurrently. Should the fix be:
> - (A) Redis distributed semaphore inside `_async_orchestrate_scrapers` (recommended), OR
> - (B) Reduce Celery concurrency to 1 in `setup_local.ps1` and use only the queue_runner gate?
> Recommendation: Option A (Redis semaphore) is architecturally correct and does not limit non-browser Celery tasks.

> [!IMPORTANT]
> **Q2 — AntiCaptcha Checkboxes Scope:** Please confirm if ALL ~20 checkboxes must be exposed in Settings UI, or only the critical 10:
> Enable AntiCaptcha, Solve reCAPTCHA v2, Invisible reCAPTCHA, reCAPTCHA v3, hCaptcha, Cloudflare Turnstile, FunCaptcha, GeeTest, Auto-Submit Form, Play Sounds.

---

## Proposed Changes

---

### SCOPE 1 — Claim Logs: "All" Unified Tab

**Plan Reference:** `IMP-2026-0919-002` (plan existed but was NEVER implemented)

**Target File:** `frontend/src/app/claims/[id]/page.tsx`

**Changes:**

1. Add `claimLogsTab` state with "all" as default:
   ```typescript
   const [claimLogsTab, setClaimLogsTab] = useState<"all"|"audit"|"processing"|"exceptions"|"terminal">("all");
   ```

2. Add `UnifiedLogItem` interface and `sortedAllLogs` useMemo that merges audit + processing + exception logs chronologically.

3. Add "All" as the FIRST tab in the tab navigation bar (icon: Layers, badge: total count).

4. Add render block for `claimLogsTab === "all"` showing each log type with color-coded source pills:
   - Audit logs → Indigo pill `AUDIT TRAIL`
   - Processing logs → Sky pill `PROCESSING`
   - Exception logs → Rose pill `EXCEPTION`

---

### SCOPE 2 — Telemetry Audit: Start/End Time Display

**Target File:** `frontend/src/app/claims/[id]/page.tsx`

**Root Cause:** The backend DOES store `start_time` and `end_time` in `claim.action_timings.portals[portalKey]` (scraper_tasks.py line 378 and 642). The frontend Telemetry Audit section does not render these fields from the portal timings object.

**Changes:**

1. In the portal timing card rendering, add start/end time display:
   ```
   Started: 14:30:22 | Ended: 14:32:45 | Duration: 143s
   ```

2. In the Telemetry Audit modal/inspection view, show `start_time` and `end_time` formatted with `new Date(ts).toLocaleTimeString()`.

---

### SCOPE 3 — Fleet Concurrency: Redis Distributed Semaphore

**Target Files:**
- `backend/app/tasks/scraper_tasks.py`

**Root Cause Analysis:**

- `queue_runner.py` reads `max_concurrent_claims` and only dispatches that many Celery tasks via the auto-queue. This is correct.
- BUT: When `bulk-start` is called directly from the Dashboard or API, it bypasses the queue_runner and dispatches ALL selected claims simultaneously. Each claim dispatch triggers one Celery task.
- Celery is configured with `--concurrency=10` (10 concurrent worker threads). Each worker picks up a task and launches ONE `SingleSessionBrowserRunner` = ONE Chrome browser.
- 10 claims dispatched simultaneously = 10 Chrome windows opening at once, regardless of `fleet=1`.

**Fix — Redis Distributed Semaphore:**

Add semaphore acquire/release helpers in `scraper_tasks.py`:

```python
BROWSER_SEMAPHORE_KEY = "uaic:browser:active_count"

async def _acquire_browser_slot(max_concurrency: int, timeout: int = 300) -> bool:
    import redis
    r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1.0, socket_timeout=1.0)
    import asyncio
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        # Atomic increment + check using Lua script
        result = r.eval(
            "local c = redis.call('incr', KEYS[1]) "
            "if c > tonumber(ARGV[1]) then redis.call('decr', KEYS[1]) return 0 end "
            "redis.call('expire', KEYS[1], 7200) return 1",
            1, BROWSER_SEMAPHORE_KEY, str(max_concurrency)
        )
        if result == 1:
            return True
        await asyncio.sleep(2)
    return False

async def _release_browser_slot():
    import redis
    r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1.0, socket_timeout=1.0)
    val = int(r.get(BROWSER_SEMAPHORE_KEY) or 0)
    if val > 0:
        r.decr(BROWSER_SEMAPHORE_KEY)
```

Usage at the top of `_async_orchestrate_scrapers` BEFORE launching the browser:

```python
max_concurrency = getattr(auto_cfg, "max_concurrent_claims", 1) or 1
slot_acquired = await _acquire_browser_slot(max_concurrency, timeout=600)
if not slot_acquired:
    claim.record_status = RecordStatusEnum.FAILED
    claim.last_error = "Timed out waiting for available browser slot (fleet concurrency limit reached)."
    await session.commit()
    return
try:
    # ... existing browser launch + scraping ...
finally:
    await _release_browser_slot()
```

**Monitor Dashboard — Pending Queue (FIFO Priority) Display:**

Currently the Monitor page shows no "Pending Queue" panel. Add:
- `StatCard` for "Pending Queue" counting claims with `record_status = NEW`, ordered by `created_at ASC`
- This makes the FIFO priority visible to operators

---

### SCOPE 4 — Monitor Table: "No. of Cases Extracted" Column

**Target File:** `frontend/src/app/monitor/page.tsx`

**Current columns:** Checkbox | Claim # | Parties | State | Overall Status | Florida Bots | Texas Bots | Duration | Actions

**Add after Duration:**

Desktop Table Header:
```tsx
<th className="py-3 px-3 cursor-pointer select-none" onClick={() => handleSort("cases_extracted")}>
  Cases Extracted {renderSortIcon("cases_extracted")}
</th>
```

Desktop Table Row Cell (after Duration `td`):
```tsx
<td className="py-3 px-3 text-center font-mono text-sm text-slate-700 dark:text-slate-300">
  {claim.action_timings?.portals
    ? Object.values(claim.action_timings.portals as Record<string, any>)
        .reduce((sum: number, p: any) => sum + (p?.cases_found ?? 0), 0)
    : (claim.scraped_cases?.length ?? 0)}
</td>
```

Also update the mobile card view and `colSpan` counts.

**Filter Addition:**
Add quick-filter buttons in the filter bar:
- "Has Matches" — shows only claims with cases_extracted > 0
- "No Matches" — shows only claims with cases_extracted = 0

---

### SCOPE 5 — AntiCaptcha Plugin Settings: Checkbox Toggles

**Target Files:**
- `backend/app/schemas/settings.py` — Add checkbox fields to `AutomationSettings`
- `backend/app/automation/browser_manager.py` — Use settings fields in `sync_api_key`
- `backend/app/automation/session_runner.py` — Pass anticaptcha_settings to browser runner
- `backend/app/tasks/scraper_tasks.py` — Pass auto_cfg to runner
- `frontend/src/types/index.ts` — Add TypeScript fields to `AutomationSettings`
- `frontend/src/app/settings/page.tsx` — Add Plugin Configuration UI section

**Backend Schema — New fields in `AutomationSettings`:**

```python
anticaptcha_enabled: bool = Field(default=True, description="Master AntiCaptcha enable/disable")
anticaptcha_auto_submit: bool = Field(default=False, description="Auto-submit form after solve")
anticaptcha_play_sounds: bool = Field(default=False, description="Play audio on solve")
anticaptcha_solve_recaptcha2: bool = Field(default=True, description="Solve reCAPTCHA v2")
anticaptcha_solve_invisible: bool = Field(default=True, description="Solve invisible reCAPTCHA")
anticaptcha_solve_recaptcha3: bool = Field(default=True, description="Solve reCAPTCHA v3")
anticaptcha_recaptcha3_score: float = Field(default=0.3, ge=0.1, le=0.9, description="reCAPTCHA v3 target score")
anticaptcha_solve_hcaptcha: bool = Field(default=True, description="Solve hCaptcha")
anticaptcha_solve_turnstile: bool = Field(default=True, description="Solve Cloudflare Turnstile")
anticaptcha_solve_funcaptcha: bool = Field(default=True, description="Solve FunCaptcha")
anticaptcha_solve_geetest: bool = Field(default=True, description="Solve GeeTest")
```

**`browser_manager.py` — Update `sync_api_key` to accept `auto_cfg`:**

Modify the hardcoded JS template to use dynamic values from `auto_cfg` fields.

**Frontend Settings Page — New Plugin Configuration section:**

Add a card section under Automation Settings with:
- Master toggle: "Enable AntiCaptcha"
- Checkboxes for each CAPTCHA type
- Auto-Submit and Play Sounds toggles
- reCAPTCHA v3 score slider (0.1–0.9)

---

### SCOPE 6 — AntiCaptcha Extension: Fix Not Loading During Extraction

**Target File:** `backend/app/automation/session_runner.py`

**Root Cause 1 — Relative Path Resolution Fails in Celery CWD:**

`settings.py` default: `chrome_extension_dir = ".\anticaptcha-plugin_v0.83\"`
In `session_runner.py`:
```python
self.extension_dir = resolve_extension_dir(extension_dir)  # from base.py
```
`base.py`'s `resolve_extension_dir` uses `os.path.abspath` relative to `__file__` which may differ from repo root when Celery runs. If the path doesn't resolve to an existing directory, `has_extension = False` and Chrome launches WITHOUT `--load-extension`.

**Root Cause 2 — Temp Profile Pre-seeding Incomplete:**

The temp profile copies only `Preferences` + `Local State`. Extension files themselves are NOT in the profile — they're loaded via `--load-extension=<path>`. But if the extension path fails to resolve, extensions are never loaded.

**Fix:**

Replace `resolve_extension_dir(extension_dir)` in `SingleSessionBrowserRunner.__init__` with `ExtensionManager.resolve_extension_path(extension_dir)` from `browser_manager.py`:

```python
from app.automation.browser_manager import ExtensionManager
from pathlib import Path

class SingleSessionBrowserRunner:
    def __init__(self, extension_dir=None, anticaptcha_api_key=None, ...):
        # Robust absolute resolution using ExtensionManager
        resolved_ext = ExtensionManager.resolve_extension_path(extension_dir)
        self.extension_dir = str(resolved_ext) if resolved_ext else None
        self.anticaptcha_api_key = anticaptcha_api_key
```

In `__aenter__` before launch, replace:
```python
# OLD:
if self.anticaptcha_api_key and has_extension:
    if getattr(SingleSessionBrowserRunner, "_last_synced_api_key", None) != self.anticaptcha_api_key:
        sync_anticaptcha_api_key(ext_norm, self.anticaptcha_api_key)
        SingleSessionBrowserRunner._last_synced_api_key = self.anticaptcha_api_key

# NEW (using ExtensionManager for full config sync):
if self.anticaptcha_api_key and has_extension:
    ExtensionManager.sync_api_key(
        extension_dir=Path(ext_norm),
        api_key=self.anticaptcha_api_key,
        auto_cfg=self.anticaptcha_settings  # None = use defaults
    )
    # Also configure and pin profile with extension
    ExtensionManager.configure_and_pin_profile(
        profile_dir=Path(self.profile_to_use),
        api_key=self.anticaptcha_api_key,
        extension_path=Path(ext_norm),
    )
```

Add `anticaptcha_settings` parameter to `SingleSessionBrowserRunner.__init__` and pass `auto_cfg` from `scraper_tasks.py`.

Add extension verification after context launch (log warning if service workers = 0).

---

## Execution Order (Priority)

> [!IMPORTANT]
> Implement in this order to fix blocking issues first:
> 1. **Scope 6** — Extension not loading (blocks all CAPTCHA solving)
> 2. **Scope 3** — Fleet concurrency (causes browser overload)
> 3. **Scope 5** — AntiCaptcha settings UI (schema + frontend)
> 4. **Scope 4** — Monitor Cases column (UI-only)
> 5. **Scope 1** — All tab in Claim Logs (UI-only)
> 6. **Scope 2** — Start/End time display (UI-only)

---

## Verification Plan

### After Each Scope — Run Full Test Suite:

```bash
# Backend
cd backend && .venv\Scripts\pytest --tb=short -q

# Python lint
cd backend && .venv\Scripts\ruff check app tests

# Frontend TypeScript
cd frontend && npx tsc --noEmit

# Frontend lint
cd frontend && npm run lint
```

### Manual Verification Per Scope:

| Scope | Test |
|---|---|
| 6 | Run extraction → AntiCaptcha icon visible in browser toolbar; CAPTCHAs solved automatically |
| 3 | Set fleet=1, bulk-start 5 claims → Only 1 Chrome window opens at a time |
| 5 | Open /settings → AntiCaptcha Plugin Configuration section visible; checkboxes persist to DB |
| 4 | Open /monitor → "Cases Extracted" column after Duration; quick filters work |
| 1 | Open /claims/[id] → "All" tab is first tab; shows merged chronological timeline |
| 2 | Open claim telemetry → Each portal shows Start Time and End Time |

---

## AI Verification Status

- [ ] Scope 6 Implemented
- [ ] Scope 3 Implemented
- [ ] Scope 5 Implemented
- [ ] Scope 4 Implemented
- [ ] Scope 1 Implemented
- [ ] Scope 2 Implemented
- [ ] All pytest: 453+ tests pass
- [ ] All ruff: 0 errors
- [ ] All tsc: 0 errors
- [ ] Manual browser verification complete
- [ ] **HUMAN VERIFIED** — Only the user can mark this ✓
