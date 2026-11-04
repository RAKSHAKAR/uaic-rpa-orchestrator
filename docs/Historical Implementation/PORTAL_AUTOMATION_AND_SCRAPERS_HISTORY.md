# Historical Implementation: Court Portal Automation & Scrapers

> **Subsystem:** County Court Portal Scrapers & Behavioral Alignment  
> **Historical Scope:** October 2026 Engineering Sprints  
> **Status:** Fully Remediated, Benchmarked & Verified  

---

## 1. Overview & Behavioral Alignment with Power Automate V4

The initial RPA implementation relied on Microsoft Power Automate Desktop (Robin desktop flows). During the Python/Playwright migration, all eight county court portal scrapers were audited against the authoritative `BotCreation_1_0_0_7` V4 Robin desktop subflows to guarantee exact behavioral parity:
- Broward County: `Subflow_Broward.robin`
- Hillsborough County: `Subflow_Hillsborough.robin`
- Miami-Dade County: `Subflow_Miami.robin`
- Travis County: `Subflow_Travis.robin`
- Dallas County: `Subflow_Dallas.robin`
- Harris County JP: `Subflow_Harris.robin`
- Harris County Clerk: `Subflow_Cclerk.robin`
- Harris County District Clerk: `Subflow_HarrisDistrict.robin`

---

## 2. Key Remediations & Technical Milestones

### 2.1 Broward County Clerk of Courts (`fl_broward`)
- **Portal URL**: `https://www.browardclerk.org/Web2`
- **Actions Implemented**:
  - Implemented multi-party triple search loop iterating through Claimant, Insured, and Driver.
  - Resolved dynamic Angular table rendering using explicit locator waits (`table#caseList tr`).
  - Implemented noise word filtering and case status normalization ("Closed", "Open", "Pending").
  - Extracted exact 5 fields: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`.
  - Added anti-detection headers and user-agent emulation to avoid Cloudflare 403 blocks.

### 2.2 Hillsborough County Clerk — HOVER (`fl_hillsborough`)
- **Portal URL**: `https://hover.hillsclerk.com/`
- **Actions Implemented**:
  - Resolved tab navigation selector flakiness where the Party Search tab (`#nav-Party-tab`) required explicit element hover before clicking.
  - Implemented business name vs individual name disambiguation.
  - Handled lazy-loaded pagination controls with custom scrolling to force table rendering.
  - Enforced 5-field schema output matching Guidewire ingestion requirements.

### 2.3 Miami-Dade County Clerk — OCS (`fl_miami`)
- **Portal URL**: `https://www2.miamidadeclerk.gov/ocs`
- **Actions Implemented**:
  - Remediated invisible Google reCAPTCHA v3 challenge verification (`g-recaptcha-response` token insertion).
  - Fixed search input form submission by triggering native DOM `change` and `blur` events on party name textboxes.
  - Extracted exact 5 fields; mapped local court types to normalized categories.

### 2.4 Dallas County Courts Portal (`te_dallas`)
- **Portal URL**: `https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29`
- **Actions Implemented**:
  - Configured Cloudflare Turnstile token injection and form submission.
  - Resolved Smart Search dropdown selection requiring simulated keyboard arrow-down and enter strokes.
  - Filtered civil and traffic cases according to filing date `>= 2010-01-01`.

### 2.5 Travis County Odyssey Portal (`te_travis`)
- **Portal URL**: `https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29`
- **Actions Implemented**:
  - Aligned Odyssey Smart Search parameters with V4 Robin flow parameters.
  - Implemented robust error recovery when search yields zero matching records, ensuring empty array `[]` is stored rather than raising unhandled exceptions.

### 2.6 Harris County Justice of the Peace (`te_harris_jp`)
- **Portal URL**: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29`
- **Actions Implemented**:
  - **Strict Schema Enforcement**: Prohibited extraction of `CaseType`. Harris JP schema is strictly **4 fields**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`.
  - Added precinct-level case filtering to isolate civil dispute filings.

### 2.7 Harris County Clerk WebSearch (`te_harris_cclerk`)
- **Portal URL**: `https://www.cclerk.hctx.net/Applications/WebSearch/`
- **Actions Implemented**:
  - **Strict Schema Enforcement**: Prohibited extraction of `CaseType`. Schema is strictly **4 fields**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`.
  - Implemented OCR and image-based CAPTCHA solving integration via Anti-Captcha `ImageToTextTask`.

### 2.8 Harris County District Clerk (`te_harris_district`)
- **Portal URL**: `https://www.hcdistrictclerk.com/cDocs/Public/Search.aspx`
- **Actions Implemented**:
  - Handled ASP.NET WebForms postback lifecycle (`__VIEWSTATE`, `__EVENTVALIDATION`).
  - Added date range boundary enforcement to limit search scope to DOL minus 2 years through present.
  - Extracted full 5 fields including `CaseType`.

---

## 3. Consolidated Output Schemas & Storage Keys

```python
# Storage Keys in SQLite Claim Record
fl_jsonbody_broward          # 5 fields
fl_jsonbody_hillsborough     # 5 fields
fl_jsonbody_miami            # 5 fields
te_jsonbody_dallas           # 5 fields
te_jsonbody_travis           # 5 fields
te_jsonbody_harris           # 4 fields (Harris JP - NO CaseType)
te_jsonbody_cclerk           # 4 fields (Harris County Clerk - NO CaseType)
te_jsonbody_hcdistrict       # 5 fields (Harris District Clerk)
```

