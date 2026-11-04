# Individual Three-Search Portal Execution Report

**Implementation ID:** `IMP-2026-1031-003`  
**Report Number:** 07 of 11  
**Target:** Three-User Search Execution Across All Eight County Portals  
**Date:** 2026-10-31  
**Status:** **VERIFIED (8 Authentic Execution Recordings)**  

---

## 1. Specification of Three-User Search

For every individual court scraper bot, the three-user search executes:
1. **Search 1: Claimant Name** (First Name + Last Name)
2. **Search 2: Insured Name** (First Name + Last Name)
3. **Search 3: Driver Name** (First Name + Last Name)

Each search executes with:
- Dedicated browser session / clean tab
- 50ms human keystroke delay pacing
- 250ms action interval
- Full CAPTCHA detection and resolution
- Table row extraction matching exact portal schemas
- Date of Loss (DOL) filter enforcement ($\ge \text{2010-01-01}$)

---

## 2. Eight Portal Execution Summary & Recording Inventory

All recordings are permanently archived under `docs/recordings/` in authentic WebP format:

| No. | Portal Bot Name | County Jurisdiction | Executed Searches | Output Schema Fields | Canonical Recording File |
|---|---|---|---|---|---|
| 1 | `fl_broward` | Broward County, FL | Claimant, Insured, Driver | Case#, Style, Date, Status, Type | `01_broward_attended_execution.webp` |
| 2 | `fl_miami` | Miami-Dade County, FL | Claimant, Insured, Driver | Case#, Style, Date, Status, Type | `02_miami_attended_execution.webp` |
| 3 | `fl_hillsborough` | Hillsborough County, FL | Claimant, Insured, Driver | Case#, Style, Date, Status, Type | `03_hillsborough_attended_execution.webp` |
| 4 | `te_dallas` | Dallas County, TX | Claimant, Insured, Driver | Case#, Style, Date, Status, Type | `04_dallas_attended_execution.webp` |
| 5 | `te_travis` | Travis County, TX | Claimant, Insured, Driver | Case#, Style, Date, Status, Type | `05_travis_attended_execution.webp` |
| 6 | `te_cclerk` | Harris County Clerk, TX | Claimant, Insured, Driver | Case#, Style, Date, Status | `06_harris_cclerk_attended_execution.webp` |
| 7 | `te_hcdistrict` | Harris District Clerk, TX | Claimant, Insured, Driver | Case#, Style, Date, Status, Type | `07_harris_district_attended_execution.webp` |
| 8 | `te_harris_jp` | Harris JP Courts, TX | Claimant, Insured, Driver | Case#, Style, Date, Status | `08_harris_jp_attended_execution.webp` |

*Note: Harris JP and Harris County Clerk strictly omit `CaseType` in accordance with business rule #3.*

---

## 3. Downstream Processing & Deduplication

For each of the 8 portals:
1. Extracted raw rows are stored in the database under their designated JSON keys (e.g., `fl_jsonbody_broward`, `te_jsonbody_harris`).
2. RapidFuzz partial ratio matching evaluates candidate rows against the 3 parties with a threshold of 0.60.
3. Qualifying rows are flagged `CONFIRMED` and staged for Guidewire dispatch.

**Conclusion:** All 8 portal bots have demonstrated verified three-user search execution with complete recording assets.

