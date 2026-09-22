# IMP-2026-0921-001 — Critical Bug Fixes: Concurrency + AntiCaptcha

**Implementation ID:** IMP-2026-0921-001  
**Priority:** CRITICAL  
**Date:** 2026-09-21

---

## Bug A — Fleet Concurrency Not Enforced (10 Chrome Despite Limit=1)

### Root Causes (3 Failures)

#### A1 — PRIMARY: `bulk-start` and `run-selected` bypass the gate entirely

[`claims.py` L1016–1025](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py#L1016-L1025):
```python
for c in claims:                     # ALL 10 claims dispatched simultaneously
    celery_app.send_task(...)        # no concurrency check at API layer
```
[`queue.py` L561–570](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/queue.py#L561-L570): same pattern.

The Redis semaphore runs **inside** each Celery task AFTER all 10 are already dispatched and running.

#### A2 — SECONDARY: Redis semaphore fails open

[`scraper_tasks.py` L127–130](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py#L127-L130):
```python
except Exception as e:
    return True   # ANY Redis error → all tasks proceed without limit
```

#### A3 — TERTIARY: Deprecated asyncio API inside `asyncio.run()` context

`asyncio.get_event_loop().time()` should be `asyncio.get_running_loop().time()`.

---

## Bug B — AntiCaptcha Not Showing/Working During Automation

> [!IMPORTANT]
> The **Browser Launch Test** works because it uses `ChromeSession` with a complete 20-key full-config CDP injection + popup activation.  
> The **actual automation** uses `SingleSessionBrowserRunner` which has an incomplete 3-key injection.

### Exact Diagnostic — What the Screenshots Show

| | Browser Launch Test (Settings) | Actual Automation (Extraction) |
|---|---|---|
| Class used | `ChromeSession` | `SingleSessionBrowserRunner` |
| Profile | Persistent `data/browser_profile/chrome/` | Temp `uaic_worker_profile_XXXX/` (clone) |
| CDP injection | **20 keys** + popup activation + balance verify | **3 keys only** (`account_key`, `auto_submit_form`, `solve_turnstile`) |
| Extension result | ✅ Active & Pinned | ❌ Not showing / inactive |

### Root Cause — Line-Level

**[`ChromeSession.start()`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py#L949-L1028)** (used by test) does:
1. Detects service worker ✅
2. Reads existing `chrome.storage.local` to check if already configured ✅
3. Injects **20-key full config** into `chrome.storage.local` AND `chrome.storage.sync` ✅
4. Opens extension popup URL (`popup_v3.html`) to initialize Vue store and verify API key balance ✅
5. Result: Extension fully activated, icon shows, CAPTCHAs solved ✅

**[`SingleSessionBrowserRunner.__aenter__()`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py#L316-L324)** (used by automation) does:
```python
# Line 320 — only 3 keys, no 'enable', no 'solve_recaptcha2', no 'account_key_checked'
await worker.evaluate(f"chrome.storage.local.set({{ 'account_key': '{self.anticaptcha_api_key}', 'auto_submit_form': false, 'solve_turnstile': true }})")
```

**Missing from `SingleSessionBrowserRunner`:**
- `enable: true` → extension disabled without this key
- `account_key_checked: true` → extension treats API key as unverified
- `solve_recaptcha2: true`, `solve_invisible_recaptcha: true`, `solve_recaptcha3: true` → CAPTCHA types not activated
- `solve_hcaptcha: true`, `solve_funcaptcha: true`, `solve_geetest: true` → additional CAPTCHA types missing
- `recaptcha3_score: 0.3` → reCAPTCHA v3 threshold missing
- Popup activation → Vue options store never initializes → extension shows as unconfigured in toolbar
- `chrome.storage.sync.set(...)` → sync storage not fully populated

Because `enable` is never set to `true`, the AntiCaptcha extension loads its service worker but **stays in its initial unconfigured state** — the toolbar icon shows as grey/inactive and CAPTCHA interception does not occur.

---

## Fix Plan

### Fix A1 — Gate dispatch at the API layer

**[`claims.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py) — `bulk_start_claims`:**
- Read `max_concurrent_claims` from DB settings
- Count active `SCRAPING_IN_PROGRESS` claims
- Dispatch only `max(0, limit - active_count)` Celery tasks; set overflow claims to `NEW` for queue runner pickup

**[`queue.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/queue.py) — `run_selected_claims`:**
- Same gate applied before dispatching selected claims

### Fix A2 — Harden semaphore: fail CLOSED

- Remove `return True` fallback in [`scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)
- Return `False` + clear FAILED error message when Redis unavailable
- Add `SEMAPHORE_BYPASS=true` env var for dev environments

### Fix A3 — `asyncio.get_running_loop()` 

Replace deprecated `asyncio.get_event_loop().time()` → `asyncio.get_running_loop().time()`

---

### Fix B — Sync SingleSessionBrowserRunner CDP Injection with ChromeSession

**[`session_runner.py` L316–324](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py#L316-L324)** — Replace the minimal 3-key injection with the complete `ChromeSession`-equivalent full-config block:

```python
# BEFORE (broken — 3 keys, extension stays inactive)
await worker.evaluate(f"chrome.storage.local.set({{ 'account_key': '{key}', 'auto_submit_form': false, 'solve_turnstile': true }})")

# AFTER (complete — 20 keys matching ChromeSession, extension fully activates)
# 1. Read existing storage to check if already configured
# 2. If not configured: inject full 20-key config to chrome.storage.local AND chrome.storage.sync
# 3. Open popup_v3.html to initialize Vue store (same as ChromeSession does for worker_id=None)
# 4. Pin extension ID in Preferences file for toolbar visibility
# 5. Log confirmation
```

The full config keys to inject (matching `ChromeSession` exactly):
```json
{
  "account_key": "<from settings>",
  "account_key_checked": true,
  "enable": true,
  "auto_submit_form": false,
  "play_sounds": false,
  "solve_recaptcha2": true,
  "solve_invisible_recaptcha": true,
  "solve_recaptcha3": true,
  "recaptcha3_score": 0.3,
  "solve_hcaptcha": true,
  "solve_turnstile": true,
  "solve_funcaptcha": true,
  "solve_geetest": true,
  "use_predefined_image_captcha_marks": true,
  "start_recaptcha2_solving_when_challenge_shown": true,
  "use_recaptcha_precaching": false,
  "k_precached_solution_count_min": 2,
  "k_precached_solution_count_max": 4,
  "dont_reuse_recaptcha_solution": false,
  "solve_proxy_on_tasks": false
}
```

Also: after injecting, **detect the actual extension ID from service worker URL** and call `pin_extension_in_preferences()` on the temp profile's `Preferences` to ensure the icon is pinned to the toolbar.

---

## Files Changed

| File | Bug | Change |
|------|-----|--------|
| [`claims.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py) | A1 | Gate bulk-start dispatch on `max_concurrent_claims` |
| [`queue.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/queue.py) | A1 | Gate run-selected dispatch |
| [`scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py) | A2, A3 | Fail-closed semaphore + `get_running_loop()` |
| [`session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py) | B | Full 20-key CDP injection + popup init + toolbar pin |

---

## Verification Plan

### Automated Tests
```bash
pytest --tb=short -q          # full regression (453 tests)
ruff check app/               # 0 errors
npx tsc --noEmit              # 0 TS errors
```

### Manual Verification — Bug A
1. Set `max_concurrent_claims = 1`
2. Bulk-start 10 claims
3. **Expected:** Only 1 Chrome window; 9 claims stay `NEW`, picked up sequentially

### Manual Verification — Bug B
1. Start a claim automation
2. **Expected:** Chrome opens with AntiCaptcha icon **green/active** in toolbar (same as Browser Launch Test)
3. **Expected:** CAPTCHAs solved automatically without manual intervention

---

> [!WARNING]
> Fix A2 (fail-closed) means: if Redis is down, claims fail with a clear error. Set `SEMAPHORE_BYPASS=true` in `.env` for dev environments without Redis.

> [!IMPORTANT]
> Fix B is a **direct port** of `ChromeSession`'s proven, working injection logic into `SingleSessionBrowserRunner`. No new logic is being invented — just bringing the automation runner up to parity with the test runner.
