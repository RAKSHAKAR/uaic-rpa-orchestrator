# Walkthrough: Broward County Court Search Submit & Glossary Table Exclusion Fix

**Implementation ID:** `IMP-2026-0930-002`  
**Date:** 2026-09-30  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Document Type:** Walkthrough (v1)  

---

## 1. Context & Identified Problem

During live browser automation on Broward County (`https://www.browardclerk.org/Web2`):
1. **CAPTCHA State:** Cloudflare Turnstile CAPTCHA showed `[✓] Verify you are human` and AntiCaptcha reported `Solved`.
2. **User Observation:** The green "Search" button (`#PersonSearchResults`) was not clicked or did not trigger submission, leaving the search form on screen.
3. **Ghost Record Creation:** The scraper recorded 12 fake "cases" for MARIA MARTINEZ (`CaseNumber: CACE`, `CaseStyle: Civil Action Central`, `CaseType: CACE15085978`).

---

## 2. Root Cause Analysis Summary

### Root Cause 1: Bootstrap FormValidation Date Rejection
On `https://www.browardclerk.org/Web2`, `filingDateOnOrAfterP` is configured with:
```javascript
filingDateOnOrAfterP: {
    row: '.col-sm-4',
    validators: {
        date: {
            message: 'Date From is invalid or an invalid date range',
            format: 'MM/DD/YYYY',
            max: 'filingDateOnOrBeforeP'
        }
    }
}
```
- In `fill_search_fields`, Date of Loss was input as `2/27/2022` (single-digit month).
- Bootstrap FormValidation's date validator strictly requires two-digit month `MM/DD/YYYY` (`02/27/2022`).
- When `#PersonSearchResults` was clicked, FormValidation intercepted the submit event, found `2/27/2022` invalid, and called `e.preventDefault()`, halting submission and preventing navigation.
- Furthermore, `filingDateOnOrAfterP` is a KendoDatePicker widget. Updating the DOM input alone did not sync Kendo's internal widget model or invoke `$('#personSearchForm').formValidation('revalidateField', 'filingDateOnOrAfterP')`.

### Root Cause 2: Static Prefix Glossary Table Trap
- On `https://www.browardclerk.org/Web2`, there is an informational static helper table (`<table class="table">`) with headers `['Case Prefix', 'Court Type', 'Example']` and rows:
  `CACE | Civil Action Central | CACE15085978`
  `COCE | County Civil Central | COCE15085978`
- In `broward.py`, Step H waited for generic `table.table tbody tr, table tbody tr`. Because this static helper table is ALREADY present on `/Web2`, `wait_for_selector` resolved instantly (0 ms).
- Step K then extracted the 12 rows from this static helper table, mistaking `CACE` for `CaseNumber` and `Civil Action Central` for `CaseStyle`.
- Step Section 4 then called `await self.return_to_search_state(page)` which reloaded `/Web2`.

---

## 3. Engineering Changes

### 1. Date Normalization Helper (`_normalize_date_to_mm_dd_yyyy`)
[broward.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/broward.py)
Normalizes any date string (`2/27/2022`, `2022-02-27`, `2/7/2022`) to strict two-digit `MM/DD/YYYY` (`02/27/2022`).

### 2. KendoDatePicker & FormValidation Revalidation
In `fill_search_fields`:
- Fills formatted DOL into the input.
- Synchronizes KendoDatePicker widget: `$(el).data('kendoDatePicker').value(dol); $(el).data('kendoDatePicker').trigger('change');`.
- Dispatches FormValidation revalidation for `lastName`, `firstName`, and `filingDateOnOrAfterP`.

### 3. Step G Search Button Pre-Validation & Submission
In Step G:
- Dispatches JavaScript pre-validation across all fields immediately before submit.
- Dispatches `#PersonSearchResults.click()` and Playwright `resilient_click(search_btn.first)`.
- Falls back to `#personSearchForm.submit()` if button click is suppressed.

### 4. Step H True Results Container Wait
In Step H:
- Waits for URL navigation away from `/Web2` towards `/CaseSearchECA/*Results*`.
- Waits for real results containers: `#divSearchResults, #divCaseSearchResults, #PersonSearchResultsTable, table:has(th:has-text('Case Number')), table tbody tr td:first-child button`.
- Strictly avoids generic table waits that match the static glossary table.

### 5. Step K Static Glossary Row Exclusion
In Step K:
- Skips any rows matching `_GLOSSARY_PREFIXES = {"CACE", "COCE", "CONO", ...}`.
- Enforces digit validation: `if not any(ch.isdigit() for ch in case_num): continue`. Real case numbers in Florida always contain year and sequence digits.
- Skips rows matching glossary descriptions (`Civil Action Central`, `County Civil Central`, `Felony`).

---

## 4. Verification Results

1. **Dedicated Test Suite:** `backend/tests/test_broward_portal.py`
   - 15/15 tests passing (100% pass rate).
   - Verified date normalization (`2/27/2022` -> `02/27/2022`).
   - Verified that static glossary rows are discarded while real cases are extracted.
2. **Backend Linting (`ruff`):**
   - 0 errors (`All checks passed!`).
3. **Frontend TypeScript (`tsc`):**
   - 0 errors (`npx tsc --noEmit` exited with code 0).
4. **PowerShell Script Syntax (`check_ps1_syntax.ps1`):**
   - 0 errors across all 12 scripts.
