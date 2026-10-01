# Implementation Plan: Broward Court Scraper Loose Selector Remediation & Direct Navigation

**Implementation ID:** `IMP-2026-0930-002`  
**Document:** `implementation_plan/2026-09-30_uaic_broward_selector_cleanup_plan_v1.md`  
**Author:** Antigravity Engineering Agent  
**Date:** 2026-09-30  
**Status:** Pending User Confirmation (NO APPROVAL = NO IMPLEMENTATION)

---

## 1. Problem Statement & User Observation

### Symptom
While observing live Attended GUI execution of Broward County court portal automation, the user observed the browser navigating to:
1. `https://www.browardclerk.org/Web2/Services/PremiumServices`
2. `https://www.browardclerk.org//Web2/CaseSearchECA/Glossary/`

The user rightly noted that the bot was not instructed to access Premium Services or Glossary, and asked why this is occurring.

---

## 2. Root Cause Analysis

### 2.1 Overly Broad Selectors in `broward.py`
In [`backend/app/automation/florida/broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py):
1. **Step B (`navigate_to_search`)** (Lines 110-120):
   ```python
   case_search_btn = page.locator(
       "div.btn-bc-ql-text:has-text('Case Search'), "
       ".btn-bc-ql-text:has-text('Case Search'), "
       ".btn-bc-ql-text, "              # <-- OVERLY BROAD: matches ALL quick links
       "a:has(div.btn-bc-ql-text), "    # <-- OVERLY BROAD: matches ALL quick link anchors
       "a:has-text('Case Search'), "
       "a[href*='CaseSearch'], "
       "a[href*='/Web2'], "             # <-- OVERLY BROAD: matches ANY link with /Web2
       "button:has-text('Case Search'), "
       "a[title*='Case Search' i]"
   )
   ```
   * On the Broward Clerk home page (`https://www.browardclerk.org/`), the first `.btn-bc-ql-text` Quick Link in the DOM is **"Premium Services"** (`/Web2/Services/PremiumServices`).
   * Because `page.locator()` evaluates these union selectors, the loose `.btn-bc-ql-text` and `a[href*='/Web2']` match the **Premium Services** card first, triggering `resilient_click()` on Premium Services!

2. **Step J (`return_to_search_state`)** (Lines 241-250):
   ```python
   case_search_btn = page.locator(
       "div.btn-bc-ql-text:has-text('Case Search'), "
       ".btn-bc-ql-text:has-text('Case Search'), "
       "a:has(div.btn-bc-ql-text), "    # <-- OVERLY BROAD
       "a:has-text('Case Search'), "
       "a[href*='CaseSearch'], "
       "a#btnNewSearch, button#btnNewSearch, "
       "a:has-text('New Search'), button:has-text('New Search'), "
       "a:has-text('Back to Search'), a:has-text('Search Again')"
   )
   ```
   * When on the search results page or returning to clean search state, the loose selector `a:has(div.btn-bc-ql-text)` matches the **"Glossary"** link in the ECA navigation header (`/Web2/CaseSearchECA/Glossary/`).
   * Clicking this sends the browser off to the Glossary page instead of resetting to the search form.

3. **Indirect Navigation**:
   * Instead of navigating directly to the authoritative Case Search URL (`https://www.browardclerk.org/Web2/CaseSearchECA/Index/` as defined in Power Automate V4), the scraper navigated to the root marketing homepage (`https://www.browardclerk.org/`), where dozens of non-court public services, marriage licenses, and premium subscription widgets compete for clicks.

---

## 3. Proposed Remediation

### 3.1 Strict Selector Scoping
In [`backend/app/automation/florida/broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py):
1. **Purge all unbounded selectors** from Step B and Step J:
   * Remove `.btn-bc-ql-text`
   * Remove `a:has(div.btn-bc-ql-text)`
   * Remove `a[href*='/Web2']`
2. **Require strict text containment** for any Case Search element:
   ```python
   case_search_btn = page.locator(
       "div.btn-bc-ql-text:has-text('Case Search'), "
       "a:has(div.btn-bc-ql-text:has-text('Case Search')), "
       "a:has-text('Case Search'), "
       "a[href*='CaseSearchECA/Index'], "
       "button:has-text('Case Search')"
   )
   ```

### 3.2 Direct Navigation to Authoritative Case Search URL
1. Update `navigate_to_search()`:
   * Always navigate directly to `https://www.browardclerk.org/Web2/CaseSearchECA/Index/`.
   * Only if the direct URL fails with an HTTP error or redirection does it fall back to the root URL and click the strictly-matched `"Case Search"` button.
2. Update `return_to_search_state()`:
   * Prefer clicking `#partyName-tab` or `#btnNewSearch` on the existing page.
   * If not visible or URL is off-course, directly navigate to `https://www.browardclerk.org/Web2/CaseSearchECA/Index/` and activate `#partyName-tab`.
   * Never click generic navbar/footer links.

---

## 4. Files Impacted

| File | Change Summary |
|---|---|
| [`backend/app/automation/florida/broward.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py) | Remove loose selectors (`.btn-bc-ql-text`, `a:has(div.btn-bc-ql-text)`, `a[href*='/Web2']`); enforce direct navigation to `Web2/CaseSearchECA/Index/` and strict text matching |
| [`backend/tests/test_broward_scraper.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_broward_scraper.py) | Unit test validating that Step B and Step J selectors do not match Premium Services or Glossary elements |

---

## 5. Verification & Testing Strategy

1. **Unit Testing**:
   * Run pytest suite: `.venv\Scripts\pytest tests/test_broward_scraper.py -v`
   * Run full 554 backend test suite: `.venv\Scripts\pytest --tb=short -q` (100% pass)
   * Verify zero Python lint issues: `.venv\Scripts\ruff check app tests`
2. **Live Visual Verification**:
   * Trigger a single Broward scraper run for a claim in Attended GUI mode.
   * Confirm on-screen that the browser navigates directly to `Web2/CaseSearchECA/Index/`, fills the party name, completes CAPTCHA, and never opens Premium Services or Glossary.

---

## 6. Definition of Done Checklist

- [ ] Loose selectors purged from `broward.py` (no `.btn-bc-ql-text` or `a[href*='/Web2']` without text filter)
- [ ] Direct navigation to `Web2/CaseSearchECA/Index/` prioritized
- [ ] Return to search state safely reloads `Web2/CaseSearchECA/Index/` without clicking stray ECA footer links
- [ ] Backend test suite 100% passing (554+ tests)
- [ ] Ruff lint 0 errors
- [ ] Frontend TypeScript clean
