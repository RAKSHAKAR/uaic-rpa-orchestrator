---
name: fl-broward-workflow
description: Complete specification and operating procedures for the Broward County Clerk of Courts (fl_broward) court scraper, CAPTCHA verification, unique names generation, and Guidewire integration.
---

# Broward County Court Scraper (`fl_broward`) Workflow Skill

## 1. Overview
The Broward County scraper (`BrowardScraper`) automates case search and discovery on the Broward County Clerk of Courts portal (`https://www.browardclerk.org/Web2`).

## 2. Business Workflow
1. **Claim Reception**: Claim arrives with policy info, dates, and party details (Insured, Driver, Claimant).
2. **Unique Names Generation**: Evaluates parties via `generate_unique_names_for_claim()` using the DualSearch/TripleSearch matrix (Insured -> Driver -> Claimant).
3. **Portal Navigation**: Navigates to `base_url`, clicks Case Search, and activates the "Party Name" tab.
4. **Data Entry**: Enters Last Name, First Name, and Date of Loss (DOL normalized to strict `MM/dd/yyyy`).
5. **CAPTCHA Verification**:
   - Inspects for Google reCAPTCHA, Cloudflare Turnstile, and AntiCaptcha extension status.
   - Waits up to configured `captcha_wait_seconds` from Settings (or 25s for mock keys).
   - Verifies solve tokens (`g-recaptcha-response > 25`, `cf-turnstile-response > 20`, or extension `.solved_flag`).
   - If unsolved, checks `has_active_captcha_challenge(page)`. If active in production mode, raises `CaptchaResolutionError`. Speculative submit is strictly blocked when an active challenge is present.
6. **Search Submission**: Clicks `#PersonSearchResults` directly.
7. **Result Extraction**:
   - Parses table rows (`table.table tbody tr`).
   - Filters out static prefix glossary rows (`CACE`, `COCE`, etc.). Real cases must contain digits.
   - Normalizes filing date to `MM/DD/YYYY`.
   - Extracts 5 exact fields: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`.
   - Traverses pagination (`a.next`, `Go to the next page`) until exhaustion.
8. **Tab Reset**: Calls `return_to_search_state(page)` to reset to a clean form for the next unique name on the same browser tab.
9. **Downstream Integration**:
   - Extracted cases saved to database and linked to `ClaimRecord`.
   - Dispatches Celery task `app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task` to the `matcher` queue for fuzzy matching cascade (Claimant -> Insured -> Driver, RapidFuzz threshold=0.60).
   - Matches pushed to Guidewire via `GuidewireClient` with formatted 9-digit `0` prefix and `CaseItems`.

