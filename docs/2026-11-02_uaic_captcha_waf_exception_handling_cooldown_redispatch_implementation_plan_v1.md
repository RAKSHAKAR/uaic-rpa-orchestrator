# UAIC CAPTCHA, WAF, Exception Handling & Automated Cooldown Re-dispatch
## Implementation Plan v1

**Implementation ID:** IMP-2026-1102-001  
**Date:** 2026-11-02  
**Status:** Approved — In Execution  
**Scope:** Enhancement to existing CAPTCHA/WAF/Cooldown framework across all 8 county portal bots

---

## 1. Gap Analysis Results

### 1.1 Existing Implementation (Verified Working)

| Component | Status | Evidence |
|---|---|---|
| `SecurityBlockException` with cooldown_seconds + portal_key | ✅ Implemented | `base.py:24-31` |
| `CaptchaResolutionError`, `PortalSearchError`, `PortalAuthenticationError` | ✅ Implemented | `base.py:34-47` |
| `detect_security_block()` (module-level, checks HTTP codes + HTML) | ✅ Implemented | `base.py:50-133` |
| `detect_security_block()` (instance method, DOM inspection) | ✅ Implemented | `base.py:1763-1875` |
| `log_security_block_event()` → security_blocks.log | ✅ Implemented | `base.py:137-158` |
| `set_portal_cooldown()` → Redis + in-memory | ✅ Implemented | `cooldown_service.py:39-78` |
| `is_portal_in_cooldown()` → Redis first, then in-memory | ✅ Implemented | `cooldown_service.py:81-117` |
| `clear_portal_cooldown()` / `clear_all_portal_cooldowns()` | ✅ Implemented | `cooldown_service.py:120-154` |
| SecurityBlockException caught in scraper loop → sets BLOCKED status | ✅ Implemented | `scraper_tasks.py:1380-1425` |
| Automated WAF lockout retry dispatch with `countdown=cooldown_delay` | ✅ Implemented | `scraper_tasks.py:1413-1418` |
| Cross-portal isolation (other portals continue when one is blocked) | ✅ Implemented | `scraper_tasks.py:921-946` |
| `retry_failed_only=True` selective re-run of FAILED/BLOCKED portals | ✅ Implemented | `scraper_tasks.py:633-640` |
| Atomic case purge before retry prevents duplicates | ✅ Implemented | `scraper_tasks.py` |
| `_dismiss_session_timeout_popup()` in BaseCourtScraper | ✅ Implemented | `base.py:1073-1086` |
| `check_and_handle_session_timeout()` in Broward/Travis/Dallas | ✅ Implemented | `broward.py:278`, `travis.py:284`, `dallas.py:270` |
| Broward: 2-attempt CAPTCHA retry loop + session timeout detection | ✅ Implemented | `broward.py:390-483` |
| Hillsborough: PerimeterX detection → SecurityBlockException(300s) | ✅ Implemented | `hillsborough.py:162-176` |
| Travis: WAF detection → SecurityBlockException | ✅ Implemented | `travis.py:188-190` |
| Dallas: CAPTCHA retry loop (max_attempts, 120s wait) | ✅ Implemented | `dallas.py:356+` |
| HumanInteractionEngine: Bézier mouse, 50ms typing delay | ✅ Implemented | `human_engine.py` |
| Stealth JS payload: navigator.webdriver override | ✅ Implemented | `browser_manager.py` |
| `retrigger_failed_cases_task` Celery Beat scheduled retry | ✅ Implemented | `retry_tasks.py` |
| **23 CAPTCHA/WAF/retry tests** → 100% pass | ✅ Verified | pytest output |

### 1.2 Identified Gaps

| Gap ID | Description | Severity | File(s) Affected |
|---|---|---|---|
| GAP-01 | No portal-specific WAF cooldown settings in `TaskQueueSettings` (Travis=600s, Hillsborough=300s hardcoded) | MEDIUM | `schemas/settings.py`, `base.py` |
| GAP-02 | Instance method `detect_security_block()` uses hardcoded cooldown values (180/300/600) not from settings | MEDIUM | `base.py:1799,1819,1834,1852,1867` |
| GAP-03 | No explicit portal health/availability check BEFORE re-dispatch after cooldown | HIGH | `scraper_tasks.py`, `cooldown_service.py` |
| GAP-04 | No structured error classification system (error codes, categories, severity levels) | MEDIUM | New: `services/error_classifier.py` |
| GAP-05 | Missing test cases: SESSION-01/02/03, WAF-01/02/03/04, REDISPATCH-01/02/03/04/05 | HIGH | New: `tests/test_captcha_waf_session_redispatch.py` |
| GAP-06 | `cooldown_service.py` missing portal operational state metadata (first_failure_ts, health_check fields) | LOW | `cooldown_service.py` |
| GAP-07 | No `CAPTCHA_DETECTED`/`AWAITING_HUMAN`/`WAF_BLOCKED`/`SESSION_EXPIRED` distinct BotStatus states | LOW | `models/claim.py` — risk of breaking existing migrations |
| GAP-08 | Worker restart: in-memory `_LOCAL_COOLDOWN_CACHE` lost on restart (Redis handles persistence OK) | LOW | `cooldown_service.py` — Redis is authoritative |

### 1.3 GAP-07 Scope Decision

> **IMPORTANT:** Adding new BotStatusEnum values requires an SQLAlchemy migration. The existing `BLOCKED` value covers WAF/PerimeterX/Rate-limit. The request's additional states (CAPTCHA_DETECTED, WAF_BLOCKED, etc.) are operational sub-states that would add complexity without changing recovery behavior. **Decision:** Extend cooldown_service metadata to carry these sub-states without changing the DB enum, preserving migration safety and backward compatibility.

---

## 2. Implementation Plan

### Phase 1: Settings Enhancement (Portal-Specific Cooldown Configuration)
Add `waf_rate_limit_cooldown_seconds`, `perimeterx_cooldown_seconds`, `ip_ban_cooldown_seconds` to `TaskQueueSettings`.

### Phase 2: Cooldown Service Enhancement (Operational State + Health Check)
Extend `cooldown_service.py` with:
- `get_portal_operational_state()` — full state metadata
- `set_portal_operational_state()` — persist structured metadata
- `check_portal_health_before_redispatch()` — blocking condition check

### Phase 3: Error Classification Service (New)
Create `backend/app/services/error_classifier.py`:
- `ErrorCode` enum (CAPTCHA_TIMEOUT, WAF_RATE_LIMIT, PERIMETERX_BLOCK, SESSION_TIMEOUT, etc.)
- `ErrorCategory` enum
- `classify_exception()` function
- `ErrorEvent` dataclass with all required fields

### Phase 4: Base Class Enhancement
Update `BaseCourtScraper.detect_security_block()` to read cooldown values from settings service instead of hardcoded values.

### Phase 5: Scraper Tasks Enhancement
- Add pre-redispatch health check before scheduling retry
- Emit structured error events through error_classifier

### Phase 6: Test Suite (Comprehensive)
Create `tests/test_captcha_waf_session_redispatch.py` with all 19 required test scenarios across 8 bots.

---

## 3. Files to Create/Modify

| File | Action | Description |
|---|---|---|
| `backend/app/services/error_classifier.py` | CREATE | Centralized error classification |
| `backend/app/services/cooldown_service.py` | MODIFY | Add operational state metadata functions |
| `backend/app/schemas/settings.py` | MODIFY | Add portal-specific cooldown config fields |
| `backend/app/automation/base.py` | MODIFY | Read cooldown from settings in detect_security_block() |
| `backend/tests/test_captcha_waf_session_redispatch.py` | CREATE | 19 new test cases per test matrix |
| `docs/Reports/CAPTCHA_ASSESSMENT_REPORT.md` | UPDATE | Full implementation evidence |

---

## 4. Test Matrix

| Test ID | Scenario | Bot Coverage | Type |
|---|---|---|---|
| CAPTCHA-01 | CAPTCHA detected | All 8 | Unit |
| CAPTCHA-02 | CAPTCHA resolved | All 8 | Unit |
| CAPTCHA-03 | CAPTCHA unresolved after 120s | Broward, Dallas, Travis | Unit |
| CAPTCHA-04 | Max CAPTCHA attempts | Broward, Dallas | Unit |
| SESSION-01 | Session timeout popup detected | Broward, Travis, Dallas | Unit |
| SESSION-02 | Session expires during search | Broward | Unit |
| SESSION-03 | Session recovery | Broward, Travis | Unit |
| WAF-01 | Travis 600s rate limit | Travis | Unit |
| WAF-02 | Hillsborough PerimeterX | Hillsborough | Unit |
| WAF-03 | Portal blocked after cooldown | All | Unit |
| WAF-04 | Portal recovers after cooldown | All | Unit |
| RETRY-01 | Retryable network failure | All | Unit |
| RETRY-02 | Non-retryable failure | All | Unit |
| REDISPATCH-01 | Cooldown expiry → re-dispatch | All | Integration |
| REDISPATCH-02 | Worker restart cooldown preserved | All | Unit |
| REDISPATCH-03 | Concurrent recovery checks | All | Unit |
| REDISPATCH-04 | One blocked, others healthy | All 8 | Integration |
| REDISPATCH-05 | No duplicate completed searches | All | Integration |
| E2E-01 | Full portal workflow | All 8 | Integration |

---

*Saved: 2026-11-02 | Author: AI Engineering (Google DeepMind Antigravity)*

