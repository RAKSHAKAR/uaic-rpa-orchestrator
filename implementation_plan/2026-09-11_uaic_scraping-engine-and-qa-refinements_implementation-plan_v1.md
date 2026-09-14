# Implementation Plan

**Implementation ID:**   IMP-2026-0911-008  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Master Scraping Engine, CAPTCHA Compliance & QA Fixes  
**Feature / Issue:**     Prompt 04 — Scraping Engine Orchestration, Anti-Captcha Management & QA Refinements  
**Document Type:**       Implementation Plan  
**Version:**             v1  
**Status:**              Approved by User (Prompt Pipeline Execution)  
**Created:**             2026-09-11  
**AI Agent:**            Antigravity (Advanced Agentic Coding)  
**Approval Status:**     Approved  
**Approved By:**         User  
**Approval Date:**       2026-09-11  
**AI Verification:**     Complete (100% Automated Testing Suite)  

---

## 1. Problem & Executive Summary

Milestone **04 - MASTER SCRAPING ENGINE, CAPTCHA COMPLIANCE & QA FIXES** focuses on:
1. **Strict Unique-Name Sequential Orchestration:**
   - Pre-open tabs for all applicable portals in parallel within a single Chrome session.
   - For each unique name derived from Insured, Driver, and Claimant, search across all open portal tabs sequentially (Name A -> Portal 1 -> Extract -> Store -> Portal 2 -> Extract -> Store ... -> Name B).
   - Once all names are searched, execute RapidFuzz deduplication and Guidewire sync.
2. **CAPTCHA Compliance & Non-Blocking Architecture:**
   - Strictly comply with reCAPTCHA/Cloudflare/Arkose terms (no spoofing, no forced bypass).
   - Graceful error capturing: mark affected portal as `FAILED`, capture full-viewport screenshot to `backend/screenshots`, record error details to database and audit logs, and continue remaining portals.
   - Support retry cooldowns and single-portal retries.
3. **Form Adjustments & Field Cleanup:**
   - Confirm `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` are removed from New/Edit forms and Ingestion Column Mapping.
4. **Canonical Default Portal URLs:**
   - Ensure all fallback strings and system defaults match the canonical 8 portal URLs:
     - Broward: `https://www.browardclerk.org/`
     - Hillsborough: `https://hover.hillsclerk.com/`
     - Miami-Dade: `https://www2.miamidadeclerk.gov/ocs`
     - Travis: `https://odysseyweb.traviscountytx.gov/Portal/`
     - Dallas: `https://courtsportal.dallascounty.org/DALLASPROD/Home/`
     - Harris JP: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`
     - CClerk: `https://www.cclerk.hctx.net/Applications/WebSearch/`
     - HCDistrict: `https://www.hcdistrictclerk.com/`
5. **Auto Queue Enabled by Default:**
   - Verify `uaic:queue:auto_mode` defaults to `true`.
6. **Scraped Cases Columns & Filing Date:**
   - Ensure `filing_date` is robustly captured and displayed across both Table View and Grouped View.
7. **AntiCaptcha Extension UI Tab:**
   - Verify dedicated AntiCaptcha Extension tab in Settings page with installation guidance, API key sync, balance check, and health diagnostics.

---

## 2. Proposed Changes

### Component 1: Backend API Fallbacks & Scraper Parity
#### [MODIFY] [backend/app/api/v1/endpoints/claims.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py)
- Update default fallback URLs in `get_claim_detail` to use clean canonical URLs for all 8 portals.

### Component 2: Scraped Cases Table Filing Date Resiliency
#### [MODIFY] [frontend/src/app/claims/[id]/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/claims/[id]/page.tsx)
- Enhance `rawDate` fallback checks in both Table and Grouped views to inspect all potential date property variations (`FilingDate`, `filing_date`, `Filing Date`, `SuitFiledDate`, `suit_filed_date`, `DateFiled`, `date_filed`).

### Component 3: Settings Page Sample Payload URL
#### [MODIFY] [frontend/src/app/settings/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- Update sample Guidewire test payload Broward URL to `https://www.browardclerk.org/`.

---

## 3. Verification Plan

### Automated Tests:
1. `cd backend; .venv\Scripts\ruff check app tests` (0 errors).
2. `cd backend; .venv\Scripts\pytest tests/test_v4_parity.py tests/test_api.py -v`.
3. `cd frontend; npx tsc --noEmit` (0 errors).
4. `cd frontend; npm run lint` (0 errors).
5. `powershell -File scripts\check_ps1_syntax.ps1` (0 errors).
