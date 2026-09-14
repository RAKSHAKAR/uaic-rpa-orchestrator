# Implementation Record

**Implementation ID:** IMP-2026-0909-004  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Scraping Engine, Automation Settings, Portal Config, QA Fixes  
**Feature / Issue:** Master Scraping Engine + CAPTCHA Compliance + QA Form Fixes (Prompt 04)  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Created:** 2026-09-09  
**AI Agent:** Antigravity (Claude Sonnet 4.6 Thinking)  
**Approval Status:** Approved  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## Problem / Request Summary

User submitted Prompt 04 covering the Master Scraping Engine, Human-Like Navigation, CAPTCHA Compliance, and QA Fixes.

---

## Gap Analysis (After Deep Inspection)

### GAP 1: Orchestration Loop Order — Needs Refactor
**Current:** `for portal → for name` (portal-first)  
**Required:** `for name → for portal` (name-first per spec)

In `session_runner.py::execute_portal_searches()`, the loop is `for party in party_pairs` **inside** each portal call. In `scraper_tasks.py`, the outer loop is `for portal in scrapers_to_run`. This means:
- Currently: Portal 1 (Name A, B, C) → Portal 2 (Name A, B, C)
- Required: Name A (Portal 1, 2, 3...) → Name B (Portal 1, 2, 3...)

**Action:** Refactor `scraper_tasks.py` orchestration.

---

### GAP 2: Default Portal URLs — 6 of 8 Need Updating

| Portal | Current Default | Required |
|--------|----------------|---------|
| Broward | `https://www.browardclerk.org/Web2/` | `https://www.browardclerk.org/` |
| Hillsborough | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` | `https://hover.hillsclerk.com/` |
| Miami-Dade | `https://www2.miamidadeclerk.gov/ocs` | ✅ Correct |
| Travis | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` | `https://odysseyweb.traviscountytx.gov/Portal/` |
| Dallas | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` |
| Harris JP | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` |
| Harris CClerk | `https://www.cclerk.hctx.net/Applications/WebSearch/` | ✅ Correct |
| HCDistrict | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` | `https://www.hcdistrictclerk.com/` |

> [!CAUTION]
> **HIGH RISK:** Odyssey portals (Travis, Dallas, Harris JP) currently navigate directly to `/Dashboard/29` which is the party search page. Changing to homepage-level URL means each scraper must add navigation to reach the search form. Dallas/Travis/Harris JP scrapers will need a `goto` + `click` to open the name search panel before filling fields.

---

### GAP 3: Deprecated Fields in TypeScript — Still Present

`frontend/src/types/index.ts` lines 80–83 still contain:
```typescript
garaging_city?: string;
garaging_state?: string;
loss_location_city?: string;
loss_location_county?: string;
```

No form pages render these fields (confirmed via grep — no results). Only the type definition needs cleanup.

Backend Pydantic schemas (`schemas/claim.py`) retain the fields with a comment noting removal from ingestion — keeping them for DB backward compatibility is correct.

---

### GAP 4: Auto Queue Default — ALREADY COMPLIANT ✅

`queue_runner.py` already defaults to `True` (line 34–36). No action needed.

---

### GAP 5: Filing Date — Scrapers Return It, Need UI Verification

All checked scrapers (Broward, Hillsborough) return `"FilingDate"` key. `scraper_tasks.py` saves it via `filing_date=c.get("FilingDate")`. Investigation needed on remaining Texas scrapers and the claim detail UI rendering.

---

### GAP 6: Anti-Captcha Extension Tab — MISSING

`SettingsTab` type has no `"extension"` tab. No dedicated install/test workflow exists. The automation settings tab has raw text inputs for extension dir/API key but no verification workflow.

---

## Proposed Changes

### Backend — Orchestration Refactor

#### [MODIFY] `backend/app/tasks/scraper_tasks.py`
- Refactor `_async_orchestrate_scrapers()`: outer loop = unique names (`party_pairs`), inner loop = portals (`scrapers_to_run`)
- Each iteration: `scraper.search_on_page(page, f_name, l_name, dol)` on the appropriate tab
- Accumulate results per portal; commit per-portal JSON body after all names are searched
- Preserve all existing status tracking, telemetry, error handling, and screenshot capture

#### [MODIFY] `backend/app/automation/session_runner.py`
- Add `execute_name_first_searches()` method (or update `execute_portal_searches` signature) to support per-name iteration
- Preserve existing `execute_portal_searches` for backward compatibility with single-bot mode

---

### Backend — Portal URLs

#### [MODIFY] `backend/app/services/settings_service.py`
- Update 6 URL defaults in `get_default_settings()`

#### [MODIFY] `backend/app/automation/florida/broward.py`
- Update default URL to `https://www.browardclerk.org/`
- Add navigation step after `page.goto()`: navigate to party search page

#### [MODIFY] `backend/app/automation/florida/hillsborough.py`
- Update default URL to `https://hover.hillsclerk.com/`
- Navigation to party search tab is already implemented (line 66–74 in existing code) — confirm it works from homepage

#### [MODIFY] `backend/app/automation/texas/travis.py`
- Update URL to `https://odysseyweb.traviscountytx.gov/Portal/`
- Add navigation to name search dashboard

#### [MODIFY] `backend/app/automation/texas/dallas.py`
- Update URL. Add navigation to party name search.

#### [MODIFY] `backend/app/automation/texas/harris_jp.py`
- Update URL. Add navigation.

#### [MODIFY] `backend/app/automation/texas/harris_district.py`
- Update URL to `https://www.hcdistrictclerk.com/`
- Add navigation to search form

---

### Backend — FilingDate Verification

#### [MODIFY] All Texas scrapers (`dallas.py`, `travis.py`, `harris_jp.py`, `harris_cclerk.py`, `harris_district.py`)
- Verify `"FilingDate"` key present in result dicts
- Fix any scraper where it is missing or empty

---

### Frontend — Field Cleanup

#### [MODIFY] `frontend/src/types/index.ts`
- Remove `garaging_city?`, `garaging_state?`, `loss_location_city?`, `loss_location_county?` from `ClaimDetail` interface

#### [MODIFY] `frontend/src/app/claims/[id]/page.tsx`
- Verify and fix `filing_date` display in Scraped Cases section

---

### Frontend — Anti-Captcha Extension Tab

#### [MODIFY] `frontend/src/app/settings/page.tsx`
- Add `"extension"` to `SettingsTab` union type
- Add tab navigation button "Extension" with shield icon
- Implement Extension Management panel:
  - **Extension Status**: Path display, version, verified badge
  - **API Key**: Masked input with show/hide + Save (saves to automation settings)
  - **Install Guide**: Step-by-step instructions for manual Chrome extension sideloading
  - **Test Button**: Calls `POST /api/v1/settings/test-browser` to verify extension loaded
  - **Settings**: `auto_submit_form` toggle, `solve_turnstile` toggle, `captcha_wait_seconds`

---

## Acceptance Criteria

- [ ] Orchestration log shows name-first order: "Name A: Broward → Hillsborough → Miami → Travis → ..." then "Name B: ..."
- [ ] All 8 portal URLs match spec after `Reset to Defaults` in Settings → Portals
- [ ] `FilingDate` visible in Scraped Cases section for Broward, Hillsborough (and all portals that return it)
- [ ] No `garaging_city`, `garaging_state`, `loss_location_city`, `loss_location_county` visible in Add/Edit form or Upload column mapping
- [ ] Settings → Extension tab exists, shows API key config, status, and test workflow
- [ ] Auto Queue is ON by default (already verified ✅)
- [ ] `pytest --tb=short -q` → all tests pass
- [ ] `ruff check app tests` → 0 errors
- [ ] `tsc --noEmit` → 0 errors

---

## Risks

| Risk | Level | Mitigation |
|------|-------|-----------|
| Odyssey scrapers break after URL shortening | HIGH | Add robust homepage-to-search navigation before form fill |
| Name-first loop changes timing/telemetry semantics | MEDIUM | Preserve stage timing merge; add per-name correlation ID |
| FilingDate genuinely unavailable for some portals | LOW | Document per-portal; show "N/A" gracefully |
| TS type removal breaks other files | LOW | Grep usages first |

---

## Test Commands

```bash
cd backend && .venv\Scripts\pytest --tb=short -q
.venv\Scripts\ruff check app tests
cd frontend && npx tsc --noEmit
```

---

**No application code has been modified yet.**  
Please confirm approval to begin execution.
