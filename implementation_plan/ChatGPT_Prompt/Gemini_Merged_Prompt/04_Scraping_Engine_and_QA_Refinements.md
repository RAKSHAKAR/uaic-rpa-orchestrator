# 04 - MASTER SCRAPING ENGINE, CAPTCHA COMPLIANCE & QA FIXES

## 1. STRICT UNIQUE-NAME ORCHESTRATION (MANDATORY)
The scraping engine must follow this exact sequence:
1. Execute the New Fuzzy Match API to generate a list of Unique Names (from Insured, Driver, and Claimant fields).
2. Open System Google Chrome with the Anti-Captcha extension. Open tabs for all applicable county portals in parallel.
3. **PROCESS ONE UNIQUE NAME AT A TIME:** 
   - Search Name A in Portal Tab 1 -> Extract -> Match -> Store.
   - Switch to Portal Tab 2 -> Search Name A -> Extract -> Match -> Store.
   - Continue until Name A is searched across ALL applicable open tabs.
4. Only after ALL tabs are searched for Name A, move to Name B.
5. After ALL unique names are fully processed, execute the existing legacy Power Automate Fuzzy Match logic.

## 2. CAPTCHA COMPLIANCE & NON-BLOCKING ARCHITECTURE
- The system must NEVER attempt to bypass, defeat, or spoof reCAPTCHA, Cloudflare, or Arkose Labs. 
- **Error Capturing:** If blocked (e.g., IP/MAC rate limit), instantly mark the site as "Failed/Blocked", capture a full-page screenshot to `.\backend\screenshots` as per structure defined in system, log details to `.\backend\logs` as per structure defined in system, and seamlessly continue processing the remaining sites.
- **Cooldown:** Implement automated retries based on portal-specific cooldowns or `Retry-After` headers.

## 3. SPECIFIC QA FIXES & FORM ADJUSTMENTS
- **Remove Fields:** Remove `Loss Location City`, `Loss Location County`, `Garaging City`, and `Garaging State` from the New Form, Edit Form, and Data Ingestion Column Mapping.
- **Default URLs:** Update default portal URLs exactly as follows:
  - Broward: `https://www.browardclerk.org/`
  - Hillsborough: `https://hover.hillsclerk.com/`
  - Miami-Dade: `https://www2.miamidadeclerk.gov/ocs`
  - Travis: `https://odysseyweb.traviscountytx.gov/Portal/`
  - Dallas: `https://courtsportal.dallascounty.org/DALLASPROD/Home/`
  - Harris JP: `https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/`
  - CClerk: `https://www.cclerk.hctx.net/Applications/WebSearch/`
  - HCDistrict: `https://www.hcdistrictclerk.com/`
- **Auto Queue:** Must be enabled by default.
- **Filing Date:** Investigate and fix the missing `Filing Date` capture in the Scraped Cases section along with other all columns.
- **Anti-Captcha Extension UI:** Create a separate workflow/UI tab in Automation Settings specifically to install and test the extension configuration prior to running queues.


Suporting Docs you can ref:
1) Security_CAPTCHA_Compliance_and_Error_Handling_Guidelines.md
2) MASTER PROMPT — COUNTY PORTAL DISCOVERY, HUMAN-LIKE NAVIGATION, CAPTCHA-SAFE AUTOMATION & VERIFIED IMPLEMENTATION.md  
3) MISSING_REQUIREMENT_CAPTCHA_COMPLIANCE_AND_RETRY_LOGIC.md  
4) County_Court_Portals_V4_Standard_Operating_Procedures.md
5) UAIC Claim & RPA Orchestrator — Corrected and Ordered Requirements.md
5) Security_Compliance_Resilience_and_FAQ.md




**Note:**

1. Most of the requirements are already implemented. **Test and verify the existing functionality before making any changes.**
2. Always focus on **upgrading, enhancing, and fixing** the existing implementation. **Do not delete or remove any existing functionality** if it is already working. If any existing functionality is not working correctly, **fix it and make it fully functional** rather than removing or replacing it unnecessarily.
