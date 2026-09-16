# Implementation Plan — Default County Court Portal URLs Update

**Implementation ID:** `IMP-2026-0917-001`  
**Date:** 2026-09-17  
**Status:** Proposed — Awaiting User Approval  
**Target Modules:** `backend/app/core/config.py`, `backend/app/schemas/settings.py`, `backend/app/services/settings_service.py`, `backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py`

---

## 1. Goal & Requirements Overview

Update the default County Court Portal URLs across configuration, schema defaults, settings service, and automated test assertions exactly as specified in Requirement #33:

| Portal | Current Default in Config/Schema | Required Default URL |
|---|---|---|
| **Broward** | `https://www.browardclerk.org/Web2/` / `.../Web2` | `https://www.browardclerk.org/` |
| **Hillsborough** | `https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab` / `.../html/caseSearch.html` | `https://hover.hillsclerk.com/` |
| **Miami-Dade** | `https://www2.miamidadeclerk.gov/ocs` | `https://www2.miamidadeclerk.gov/ocs` |
| **Travis** | `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29` / `.../CourtDirectorySearch/` | `https://odysseyweb.traviscountytx.gov/Portal/` |
| **Dallas** | `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29` / `.../DALLASPROD/` | `https://courtsportal.dallascounty.org/DALLASPROD/Home/` |
| **Harris JP** | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29` / `.../CivilSearch.aspx` | `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/` |
| **CClerk** | `https://www.cclerk.hctx.net/Applications/WebSearch/` | `https://www.cclerk.hctx.net/Applications/WebSearch/` |
| **HCDistrict** | `https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx` / `.../CaseDetails.aspx` | `https://www.hcdistrictclerk.com/` |

---

## 2. Technical Architecture & Analysis

1. **Scraper Compatibility Confirmed:**
   - All 8 scrapers in `backend/app/automation/` (`broward.py`, `hillsborough.py`, `miami.py`, `travis.py`, `dallas.py`, `harris_jp.py`, `harris_cclerk.py`, `harris_district.py`) already support these clean base URLs and dynamically construct their deep search paths:
     - `BrowardScraper`: accepts `https://www.browardclerk.org/`, appends `/Web2/CaseSearchECA/Index/` during navigation.
     - `HillsboroughScraper`: accepts `https://hover.hillsclerk.com/`, appends `/html/case/caseSearch.html#nav-Party-tab`.
     - `TravisScraper`: accepts `https://odysseyweb.traviscountytx.gov/Portal/`, appends `/Home/Dashboard/29`.
     - `DallasScraper`: accepts `https://courtsportal.dallascounty.org/DALLASPROD/Home/`, appends `/Dashboard/29`.
     - `HarrisJPScraper`: accepts `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`, appends `/Dashboard/29`.
     - `HarrisDistrictClerkScraper`: accepts `https://www.hcdistrictclerk.com/`, appends `/eDocs/Public/Search.aspx`.

2. **Redis & Runtime Persistence Migration:**
   - `get_system_settings_async()` and `get_system_settings_sync()` read from Redis key `uaic:system:settings:v4`.
   - We will add an automatic URL sanitizer/migrator in `settings_service.py` so that any existing Redis cache holding legacy URLs seamlessly updates to the new required defaults upon reading or resetting.

---

## 3. Proposed Changes

### Component 1: Environment & Core Configuration
#### [MODIFY] [backend/app/core/config.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/core/config.py)
Update lines 73–80 to define the exact 8 default URL constants:
```python
    # Portals
    PORTAL_BROWARD_URL: str = "https://www.browardclerk.org/"
    PORTAL_HILLSBOROUGH_URL: str = "https://hover.hillsclerk.com/"
    PORTAL_MIAMI_URL: str = "https://www2.miamidadeclerk.gov/ocs"
    PORTAL_TRAVIS_URL: str = "https://odysseyweb.traviscountytx.gov/Portal/"
    PORTAL_DALLAS_URL: str = "https://courtsportal.dallascounty.org/DALLASPROD/Home/"
    PORTAL_HARRIS_JP_URL: str = "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/"
    PORTAL_HARRIS_CCLERK_URL: str = "https://www.cclerk.hctx.net/Applications/WebSearch/"
    PORTAL_HARRIS_DISTRICT_URL: str = "https://www.hcdistrictclerk.com/"
```

### Component 2: Pydantic Schema Defaults
#### [MODIFY] [backend/app/schemas/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py)
Update `PortalsSettings` field defaults for `broward_url`, `hillsborough_url`, `miami_url`, `travis_url`, `dallas_url`, `harris_jp_url`, `harris_cclerk_url`, and `harris_district_url`.

### Component 3: Dynamic Settings Service & Redis Migration
#### [MODIFY] [backend/app/services/settings_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/settings_service.py)
- Update `get_default_settings()` PortalsSettings fallbacks with the new defaults.
- In `get_system_settings_async` / `get_system_settings_sync`, check `portals_data` and automatically migrate legacy URLs to the new required defaults.

### Component 4: Test Suite Alignment
#### [MODIFY] [backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py)
Update `test_p4_004_exact_default_portal_urls` to assert the 8 new default URLs.

---

## 4. Verification Plan

### Automated Tests
1. **Targeted Portal URL Test:**
   ```bash
   backend/.venv/Scripts/pytest backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py -k test_p4_004 -v
   ```
2. **Full Backend Pytest Suite:**
   ```bash
   backend/.venv/Scripts/pytest -q
   ```
3. **Backend Linting:**
   ```bash
   backend/.venv/Scripts/ruff check app tests
   ```
4. **Frontend Type Check:**
   ```bash
   frontend/npx tsc --noEmit
   ```
5. **Frontend Lint:**
   ```bash
   frontend/npm run lint
   ```

### Visual Verification
- Inspect the `/settings` Court Portals configuration cards in the browser to verify that all 8 portal URLs display the new defaults.
