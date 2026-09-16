# Implementation Plan — Default County Court Portal URLs Update

**Implementation ID:** `IMP-2026-0917-001`  
**Date:** 2026-09-17  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Target Modules:** `backend/app/core/config.py`, `backend/app/schemas/settings.py`, `backend/app/services/settings_service.py`, `backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py`

---

## 1. Goal & Requirements Overview

Update the default County Court Portal URLs across configuration, schema defaults, settings service, and automated test assertions exactly as specified in Requirement #33:

| Portal | Previous Value | Required & Applied Default URL | Status |
|---|---|---|---|
| **Broward** | `https://www.browardclerk.org/Web2` | `https://www.browardclerk.org/` | Verified |
| **Hillsborough** | `https://hover.hillsclerk.com/html/caseSearch.html` | `https://hover.hillsclerk.com/` | Verified |
| **Miami-Dade** | `https://onlineservices.miami-dadeclerk.com/civil/` | `https://www2.miamidadeclerk.gov/ocs` | Verified |
| **Travis** | `https://odysseypa.traviscountytx.gov/CourtDirectorySearch/` | `https://odysseyweb.traviscountytx.gov/Portal/` | Verified |
| **Dallas** | `https://courtsportal.dallascounty.org/DALLASPROD/` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` | Verified |
| **Harris JP** | `https://jpwebsite.harriscountytx.gov/Public/CivilSearch.aspx` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` | Verified |
| **CClerk** | `https://www.cclerk.hctx.net/applications/websearch/courtsearch.aspx?CaseType=Civil` | `https://www.cclerk.hctx.net/Applications/WebSearch/` | Verified |
| **HCDistrict** | `https://www.hcdistrictclerk.com/edocs/public/CaseDetails.aspx` | `https://www.hcdistrictclerk.com/` | Verified |

---

## 2. Technical Architecture & Analysis

1. **Scraper Compatibility Confirmed:**
   - All 8 scrapers in `backend/app/automation/` (`broward.py`, `hillsborough.py`, `miami.py`, `travis.py`, `dallas.py`, `harris_jp.py`, `harris_cclerk.py`, `harris_district.py`) already support these clean base URLs and dynamically construct their deep search paths.

2. **Redis & Runtime Persistence Migration:**
   - `get_system_settings_async()` and `get_system_settings_sync()` read from Redis key `uaic:system:settings:v4`.
   - Added `_normalize_portals_data` migration in `settings_service.py` so that any existing Redis cache or persisted state holding legacy URLs automatically upgrades to the new required defaults upon reading or loading.
   - Synchronized active Redis key `uaic:system:settings:v4` directly so the live `/settings` UI immediately displays the updated values without requiring a full cache clear.

---

## 3. Applied Changes

### Component 1: Environment & Core Configuration
- [backend/app/core/config.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/core/config.py):
  Updated `PORTAL_*_URL` constants for Broward, Hillsborough, Miami, Travis, Dallas, Harris JP, CClerk, and HCDistrict.

### Component 2: Pydantic Schema Defaults
- [backend/app/schemas/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py):
  Updated `PortalsSettings` schema field defaults to the 8 required URLs.

### Component 3: Dynamic Settings Service & Redis Migration
- [backend/app/services/settings_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/settings_service.py):
  - Updated `get_default_settings()` PortalsSettings fallbacks.
  - Implemented `_normalize_portals_data` helper in `get_system_settings_async` and `get_system_settings_sync` to automatically normalize legacy URLs in stored Redis JSON.

### Component 4: Test Suite Alignment
- [backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py):
  Updated `test_p4_004_exact_default_portal_urls` to assert the 8 new default URLs.

---

## 4. Verification & Validation Evidence

### Automated Tests
1. **Targeted Test (`test_p4_004_exact_default_portal_urls`):** Passed (8/8 in suite).
2. **Full Backend Pytest Suite:** All 439 tests passed across 32 test suites (0 failures).
3. **Backend Lint (`ruff check app tests`):** 0 errors.
4. **Frontend TypeScript (`npx tsc --noEmit`):** 0 errors.
5. **PowerShell Syntax Check (`check_ps1_syntax.ps1`):** 0 errors.

### Live Visual Evidence
- **Screenshot:** [implementation_plan/Images/portal_default_urls_settings.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/portal_default_urls_settings.png)
- **Browser Subagent Video:** [implementation_plan/Recording/verify_settings_portal_urls.webp](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Recording/verify_settings_portal_urls.webp)
