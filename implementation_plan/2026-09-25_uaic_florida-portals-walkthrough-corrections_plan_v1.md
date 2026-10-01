# Implementation Plan — Florida Portals Automation Corrections (Manual Walkthrough Verification)

**Implementation ID:** `IMP-2026-0925-001`  
**Date:** 2026-09-25  
**Version:** v1  
**Status:** Approved by User  
**Target Systems:** `backend/app/automation/base.py`, `backend/app/automation/florida/broward.py`, `backend/app/automation/florida/hillsborough.py`, `backend/app/automation/florida/miami.py`

---

## 1. Context & Objectives

During the live manual walkthrough demonstration, the user executed a complete search for **1 claim record with 3 unique names** across all 3 Florida court portals (**Broward**, **Hillsborough**, and **Miami-Dade**).

### Specific Human Feedback & Root Causes:
1. **Broward (`broward.py`):**
   * *User Finding:* `broward.py` was working fine, but when an **image CAPTCHA** was presented, AntiCaptcha solved the challenge, but the image challenge popup overlay (`bframe` / challenge iframe) was not being dismissed because the bot did not perform an **outside click** to close the image part.
   * *Solution:* Implement `dismiss_captcha_challenge_popup()` in `BaseCourtScraper` and call it both inside the solver loop and directly before `#PersonSearchResults` submission in `broward.py`.

2. **Hillsborough (`hillsborough.py`):**
   * *Observed Manual Flow:* Must explicitly select the **Party Search Tab** (`#nav-Party-tab`) before entering First/Last names, and click the submit button located specifically inside the `#nav-Party` pane (`#btnSubmitPartySearch`), transitioning to `searchResults.html`.
   * *Solution:* Enforce `#nav-Party-tab` activation and down search button targeting with full pagination extraction.

3. **Miami-Dade (`miami.py`):**
   * *Observed Manual Flow:* Navigation traverses the user management gateway (`/usermanagementservices/?hs=OCSB`) before search execution on `/ocs/searchResults`.
   * *Solution:* Handle user management agreement/gateway acknowledgment so session tokens remain valid, then extract all columns across all pagination pages.

---

## 2. Technical Scope of Changes

### A. `backend/app/automation/base.py`
* Implement `dismiss_captcha_challenge_popup(self, page: Page)` on `BaseCourtScraper`:
  1. Inspects DOM for active challenge frames: `iframe[title*='challenge' i]`, `iframe[src*='bframe']`, `.rc-imageselect`.
  2. Dispatches mouse click at `(50, 50)` (top-left margin outside popup).
  3. Sends `Escape` key press.
  4. Clicks outside page container/header if popup is still anchored.
  5. Waits for DOM settling.
* Call `await self.dismiss_captcha_challenge_popup(page)` in `detect_and_handle_captcha()` immediately after solve verification.

### B. `backend/app/automation/florida/broward.py`
* In `search_by_party_name`:
  * After `detect_and_handle_captcha`, call `await self.dismiss_captcha_challenge_popup(page)`.
  * Prior to clicking `#PersonSearchResults` (Step H), re-invoke `await self.dismiss_captcha_challenge_popup(page)` to ensure the submit button is completely unblocked.

### C. `backend/app/automation/florida/hillsborough.py`
* In `select_party_search_tab`:
  * Always click `#nav-Party-tab` and wait for `#spLastName` readiness.
* In `search_by_party_name`:
  * Click `#nav-Party #btnSubmitPartySearch` (down search button).
  * Invoke `await self.dismiss_captcha_challenge_popup(page)` post-CAPTCHA.
  * Extract all results and traverse DataTables pagination.

### D. `backend/app/automation/florida/miami.py`
* In `navigate_to_search` / `verify_portal_url`:
  * Detect and clear `/usermanagementservices/?hs=OCSB` gateway agreement.
* Invoke `await self.dismiss_captcha_challenge_popup(page)` post-CAPTCHA.
* Extract all columns from table and handle pagination.

---

## 3. Verification & Validation Protocol

1. **Static Analysis & Lint:**
   * `ruff check app tests` (0 errors)
   * `npx tsc --noEmit` (0 errors)
   * `scripts\check_ps1_syntax.ps1` (0 errors)
2. **Automated Unit & Integration Tests:**
   * `pytest --tb=short -q` (All backend tests passing)
3. **Documentation:**
   * Final Implementation Record saved to `implementation_plan/`
   * Update `README.md`
