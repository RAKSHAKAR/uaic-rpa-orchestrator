# 04 - MASTER SCRAPING ENGINE, HUMAN-LIKE NAVIGATION & CAPTCHA COMPLIANCE

## 1. STRICT UNIQUE-NAME ORCHESTRATION (MANDATORY SEQUENCE)
The scraping engine must follow this exact sequence:

1. **Generate Unique Names:** Execute the New Fuzzy Match API to generate a list of Unique Names (from Insured, Driver, and Claimant fields).
2. **Launch & Route:** Open the configured default browser (System Chrome/Edge/Chromium) with the Anti-Captcha extension loaded. Open tabs for all applicable portals based on routing rules:
   - **Florida:** Broward, Hillsborough, Miami-Dade.
   - **Texas:** Travis, Dallas, Harris JP, CClerk, HCDistrict.
   - **Cross-State / Policy State != Loss Location State:** All 8 portals (All Florida + All Texas).
3. **CRITICAL — PROCESS ONE UNIQUE NAME AT A TIME:** 
   - Search the *current unique name (e.g., Name A)* across all opened applicable portal tabs sequentially.
   - **Per-Portal Flow:** 
     - Fill data into the required fields (First Name, Last Name, Date From, etc.). 
     - Detect CAPTCHA/Security challenge. If Anti-Captcha is not auto-processing, click the checkbox for reCAPTCHA/Cloudflare/etc..
     - Wait for the CAPTCHA to be solved and verified by the Anti-Captcha extension. 
     - Captcha settings in Automation Settings must be applied/implemented if missing.
     - Click the Search/Submit button *only after* successful verification. 
     - Wait for the Search Result page to fully load. 
     - Extract all case data (including all paginated data). 
     - Match the extracted cases against the original claim data. 
     - Store the matched results.
   - Switch to Portal Tab 2 -> Repeat the Search/Extract/Match/Store flow for Name A.
   - Continue until Name A is searched across ALL applicable open tabs.
4. **Next Name:** Only after ALL tabs are searched for Name A, move to Name B.
5. **Final Match:** After ALL unique names are fully processed across all applicable tabs, execute the existing legacy Power Automate Fuzzy Match logic.
6. **Guidewire Integration:** Create the JSON payload or required data structure using the output of Step 5 and send it to the Guidewire system.
7. **Audit & Logs:** Maintain detailed logs, correlation IDs, and execution telemetry for every step (start, search, CAPTCHA status, extraction, completion) for audit and compliance purposes.
Note: Sometime(s), the controls or componenet or the things you are looking for in the page where you are currently that is not basically in that page, you have to think like humnan and check the things that controls basically belogngs to which place and which url or which step then you havae to move there to work continiue.

## 2. CAPTCHA COMPLIANCE, SECURITY HANDLING (MISSING REQUIREMENT INJECTED) & NON-BLOCKING ARCHITECTURE
- The system must NEVER attempt to bypass, defeat, or circumvent/spoof reCAPTCHA, Cloudflare, or Arkose Labs.
- Detect security challenges. Pause automation. Allow an authorized human to complete the challenge in Attended mode.
- **Non-Blocking Architecture/Error Capturing:** If blocked (IP/MAC/Rate Limit), mark the site as "Failed/Blocked", capture a full-page screenshot to `.\backend\screenshots`, log to `.\backend\logs`, and seamlessly continue processing the remaining sites.
- **Cooldown:** Implement automated retries based on portal-specific cooldowns or `Retry-After` headers.

## 3. SPECIFIC QA FIXES & FORM ADJUSTMENTS
- **Remove Fields:** Remove `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` from the New Form, Edit Form, and Data Ingestion Column Mapping.
- **Default PORTAL URLs:** Update default portal URLs exactly as follows:
  - Broward: `https://www.browardclerk.org/`
  - Hillsborough: `https://hover.hillsclerk.com/`
  - Miami-Dade: `https://www2.miamidadeclerk.gov/ocs`
  - Travis: `https://odysseyweb.traviscountytx.gov/Portal/`
  - Dallas: `https://courtsportal.dallascounty.org/DALLASPROD/Home/`
  - Harris JP: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`
  - CClerk: `https://www.cclerk.hctx.net/Applications/WebSearch/`
  - HCDistrict: `https://www.hcdistrictclerk.com/`
- **Auto Queue:** Must be enabled by default.
- **Filing Date:** Investigate and fix the missing `Filing Date` capture in the Scraped Cases section.
- **Anti-Captcha Extension UI:** Create a separate workflow/UI tab in Automation Settings specifically to install and test the extension configuration prior to running queues.

Supporting Docs you can ref:
    1) Security_CAPTCHA_Compliance_and_Error_Handling_Guidelines.md
    2) MASTER PROMPT — COUNTY PORTAL DISCOVERY, HUMAN-LIKE NAVIGATION, CAPTCHA-SAFE AUTOMATION & VERIFIED IMPLEMENTATION.md
    3) MISSING_REQUIREMENT_CAPTCHA_COMPLIANCE_AND_RETRY_LOGIC.md
    4) UAIC Claim & RPA Orchestrator — Corrected and Ordered Requirements.md
    5) County_Court_Portals_V4_Standard_Operating_Procedures.md
Note: Most of them are already implemented, test before making any changes.