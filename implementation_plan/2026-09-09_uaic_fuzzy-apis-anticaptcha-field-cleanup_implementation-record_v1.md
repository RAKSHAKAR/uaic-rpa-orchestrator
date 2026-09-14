# IMP-2026-0909-003 — Implementation Record
**UAIC: Fuzzy Match APIs · Anti-Captcha Endpoint · Deprecated Field Cleanup**
*Created: 2026-09-09 | Status: Complete | AI Verification: Complete (100% Automated Testing Suite)*

---

## Change Log

### Backend — `backend/app/`

| File | Type | Description |
|------|------|-------------|
| `schemas/match.py` | MODIFY | Added `FuzzyMatchItem`, `FuzzySearchRequest`, `FuzzySearchResponse`, `ExtractNamesResponse` Pydantic schemas |
| `api/v1/endpoints/matches.py` | MODIFY | Added `GET /extract-names` and `POST /fuzzy-search` routes |
| `api/v1/endpoints/settings.py` | MODIFY | Added `POST /test-anticaptcha` route; uses `httpx.AsyncClient` (no new deps) |
| `schemas/claim.py` | MODIFY | Removed 4 deprecated ingestion aliases from `ClaimRowSchema` |

### Frontend — `frontend/src/`

| File | Type | Description |
|------|------|-------------|
| `types/index.ts` | MODIFY | Added 5 new TypeScript interfaces |
| `lib/api.ts` | MODIFY | Added 3 new typed API methods |
| `app/monitor/page.tsx` | MODIFY | Removed deprecated fields from 7 locations (state, handlers, JSX) |
| `app/claims/[id]/page.tsx` | MODIFY | Removed deprecated fields from 3 locations; confirmed modals wired |
| `app/settings/page.tsx` | MODIFY | Added Anti-Captcha balance test card + handler + result display |

### Tests — `backend/tests/`

| File | Type | Description |
|------|------|-------------|
| `tests/test_imp_2026_0909_003.py` | NEW | 32 automated tests for all 3 new endpoints + schema cleanup |
| `tests/test_plan_verification.py` | FIX | Fixed pre-existing flaky test `test_queue_runner_progression_and_recovery` — wrong patch target + stale Redis lock |

---

## Test Report

| Gate | Result |
|------|--------|
| `ruff check app` | ✅ 0 errors |
| `tsc --noEmit` | ✅ 0 errors |
| `pytest tests/test_imp_2026_0909_003.py` | ✅ 32/32 passed |
| `pytest` (full suite) | ✅ **214/214 passed, 0 failures** |
| `npm run build` | ✅ exit 0, 10 routes compiled |

---

## New Test Coverage Detail

### `GET /api/v1/matches/extract-names` — 8 tests
- Empty DB returns valid empty response
- Seeded first+last names appear in correct party list
- `?party_type=insured/driver/claimant` filters work correctly
- Duplicate names deduplicated to single entry
- Names are sorted alphabetically
- `total` equals sum of all three lists

### `POST /api/v1/matches/fuzzy-search` — 11 tests
- Missing `search_name` → 422
- Blank `search_name` → 422
- No matches → `total=0`, all response fields present
- High-similarity seeded case appears above threshold
- All response schema fields present (`court_case_id`, `case_number`, `case_style`, `county_name`, `filing_date`, `case_status`, `similarity_score`)
- Results sorted by similarity descending
- `limit` param caps results
- Threshold 0.99 excludes low-similarity cases
- Default `threshold_applied == 0.6` when omitted
- `min_filing_year=2010` excludes pre-2010 cases
- `duration_ms >= 0` always present
- `search_name` echoed back (stripped)

### `POST /api/v1/settings/test-anticaptcha` — 7 tests (all mocked — no network)
- Missing body → 422
- Blank `api_key` → 422
- Mocked success → `status=ok`, balance, `error_code=None`
- Mocked API error → `status=error`, correct `error_code`
- `TimeoutError` → `error_code=TIMEOUT`
- `OSError` → `error_code=CONNECTION_ERROR`
- `latency_ms` always present and ≥ 0

### `ClaimRowSchema` cleanup — 5 unit tests
- 4 deprecated fields absent from `model_fields`
- 4 deprecated Excel aliases absent from schema
- 10 core fields still present
- Row without deprecated cols validates cleanly
- ORM table still has all 4 deprecated columns

---

## Pre-Existing Bug Fixed

**`test_plan_verification.py::test_queue_runner_progression_and_recovery`**

- **Root cause 1:** Wrong mock patch target. `queue_runner.py` imports `celery_app` at module level and calls it as `celery_app.send_task()` directly. The test patched `"app.core.celery_app.celery_app.send_task"` (the source object) but the function holds a reference to the already-imported name in `app.tasks.queue_runner` namespace. Fixed to `"app.tasks.queue_runner.celery_app.send_task"`.
- **Root cause 2:** Stale Redis lock from prior runs could leave `active_queue_item_id` set, causing `_async_advance_auto_queue` to see 0 available slots. Fixed by calling `set_active_queue_item_id("")` immediately before enabling auto-queue in the test.

---

## Business Rule Preservation

- ✅ Guidewire payload contract unchanged
- ✅ State routing logic (FL/TX/cross-state) unchanged
- ✅ DOL date base (1899-12-30) unchanged
- ✅ Claim number prefix rule (9-digit → prepend "0") unchanged
- ✅ Fuzzy match cascade (Claimant → Insured → Driver) in `fuzzy_tasks.py` untouched; `/fuzzy-search` is additive read-only
- ✅ DB model fields (`garaging_city`, `garaging_state`, `loss_location_city`, `loss_location_county`) remain in `ClaimRecord`
- ✅ Portal output schemas exact (no CaseType for Harris JP / Harris Clerk)
- ✅ All 182 original tests continue to pass + 32 new tests added = 214 total
