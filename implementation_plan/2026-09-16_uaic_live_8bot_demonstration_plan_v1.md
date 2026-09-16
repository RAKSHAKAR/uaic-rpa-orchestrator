# Implementation Plan: Live 8-Portal End-to-End Demonstration on 2 Cross-State Claims

**Implementation ID:** `IMP-2026-0916-003`  
**Date:** September 16, 2026  
**Status:** Approved - In Execution  

---

## 1. Goal Description
The user requested a live, step-by-step demonstration of at least **2 claim records** processed across **all 8 County Court Portal bots**:
1. **Florida Portals (3):** Broward County, Hillsborough County, Miami-Dade County.
2. **Texas Portals (5):** Travis County, Dallas County, Harris JP, Harris County Clerk, Harris District Clerk.

The demonstration provides full transparency into:
1. **Live Navigation:** Loading portal base URLs, menu hover/navigation (e.g. Harris Clerk `COURTS` -> `County Civil`), form field targeting, and biometric keystroke typing.
2. **CAPTCHA Wait & Resolution:** DOM scanning for reCAPTCHA v2 / Turnstile / hCaptcha / AntiCaptcha status, active polling of `.antigate_solver.in_process`, token verification (`g-recaptcha-response` > 25 chars, `cf-turnstile-response` > 20 chars), and settling delay before submission.
3. **Docket Extraction & Strict Schemas:** Multi-page result pagination, docket row extraction conforming to strict schemas (strictly **NO** `CaseType` on Harris JP and Harris County Clerk; **WITH** `CaseType` on the other 6 portals).
4. **RapidFuzz 3-Tier Matching Cascade:**
   - Tier 1: Claimant First + Last against `CaseStyle` (threshold 0.60).
   - Tier 2: Insured First + Last against `CaseStyle` (threshold 0.60).
   - Tier 3: Driver First + Last against `CaseStyle` (threshold 0.60).
5. **Guidewire Cloud Integration:**
   - Applying the 9-digit `'0'` prefix rule (`987654321` -> `0987654321`).
   - Generating standard Guidewire contract JSON payload.
   - Dispatching payload to Guidewire Client, receiving `activityId`, persisting audit records, and updating UI claim status to `COMPLETED` / `MATCH_FOUND`.

---

## 2. Target Test Records Specification

Under authoritative business rules, cross-state claims (`policy_state != loss_location_state`) trigger **ALL 8** portals automatically:

### Record 1: `CLM-LIVE-DEMO-01`
- **Claim Number:** `987654321` (9 digits -> verifies Guidewire `'0'` prefix rule -> `0987654321`)
- **Policy State:** `FL`
- **Loss Location State:** `TX` (Cross-state -> routes to all 8 bots)
- **DOL:** `05/14/2023`
- **Insured:** `Carlos Hernandez`
- **Driver:** `Juan Ramirez`
- **Claimant:** `John Doe`
- **Search Count Derivation:** All 3 distinct -> DualSearch = 2, TripleSearch = 3 (searches Insured, Driver, Claimant across tabs).

### Record 2: `CLM-LIVE-DEMO-02`
- **Claim Number:** `123456789` (9 digits -> verifies Guidewire `'0'` prefix rule -> `0123456789`)
- **Policy State:** `TX`
- **Loss Location State:** `FL` (Cross-state -> routes to all 8 bots)
- **DOL:** `10/20/2022`
- **Insured:** `Sam Wilson`
- **Driver:** `Steve Rogers`
- **Claimant:** `Maria Lopez`
- **Search Count Derivation:** All 3 distinct -> DualSearch = 2, TripleSearch = 3 (searches Insured, Driver, Claimant across tabs).

---

## 3. Proposed Execution Architecture

### Script: `backend/app/scripts/run_live_demo_8bots.py`
A comprehensive, standalone live demonstration runner that:
1. Ingests or seeds the 2 cross-state test claims into PostgreSQL.
2. Initializes the single-session Chrome browser runner across all 8 portals.
3. Streams real-time, color-coded console logs for:
   - Navigation URLs and menu clicks.
   - CAPTCHA detection, tokens, and wait loops.
   - Case counts, docket rows, and schema field verification.
   - RapidFuzz candidate scores across Claimant, Insured, and Driver.
   - The exact JSON payload sent to Guidewire and the received response / `ActivityID`.
4. Saves full execution logs to `backend/logs/{claim_id}/{portal}/execution.log`.
5. Takes viewport verification screenshots stored into `implementation_plan/Images/`.
6. Opens the Frontend Claim Detail view (`http://localhost:3000/claims/{id}`) to verify that stages, dockets, and Guidewire payloads are displayed in the UI.

---

## 4. Verification Plan

### Automated / Diagnostic Execution
- Execute `backend\app\scripts\run_live_demo_8bots.py` with Python 3.14.7 venv.
- Verify schema integrity: ensure Harris JP and Harris Clerk outputs contain zero `CaseType` fields.
- Verify Guidewire payload: ensure `ClaimNumber` is properly prefixed to 10 digits (`0987654321` and `0123456789`).
- Check database state: verify `ScrapedCourtCase`, `MatchPair`, `GuidewireActivity`, and `ClaimRecord` rows.

### Live Browser & Visual Verification
- Observe browser navigation and CAPTCHA handling.
- Verify Frontend UI routes (`/claims/:id`, `/monitor`, `/audit`).
- Capture screenshots and log files into `implementation_plan/`.
